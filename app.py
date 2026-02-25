import streamlit as st
import sqlite3

# --- 1. データベース処理 ---
def init_db():
    conn = sqlite3.connect('shopping_list.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, current INTEGER, needed INTEGER)''')
    conn.commit()
    return conn

conn = init_db()

def get_items():
    c = conn.cursor()
    c.execute("SELECT id, name, current, needed FROM items")
    return c.fetchall()

def add_item(name, current, needed):
    c = conn.cursor()
    c.execute("INSERT INTO items (name, current, needed) VALUES (?, ?, ?)", (name, current, needed))
    conn.commit()

def update_item_fields(item_id, current, needed):
    c = conn.cursor()
    c.execute("UPDATE items SET current = ?, needed = ? WHERE id = ?", (current, needed, item_id))
    conn.commit()

def delete_item(item_id):
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()

# --- 2. コールバック関数（即時反映） ---
def buy_item(idx, curr, need):
    new_curr = min(curr + need, 15)
    update_item_fields(idx, new_curr, 0)
    st.session_state[f"c_{idx}"] = new_curr
    st.session_state[f"n_{idx}"] = 0

def update_qty(idx, curr_key, need_key):
    new_c = st.session_state[curr_key]
    new_n = st.session_state[need_key]
    update_item_fields(idx, new_c, new_n)

def delete_item_callback(idx):
    delete_item(idx)


# --- 3. UI設定 & 隙間ゼロCSS ---
st.set_page_config(page_title="買い物リスト", layout="centered")

st.markdown("""
<style>
/* 画面の横スクロールを完全に防ぐ */
html, body, [data-testid="stAppViewContainer"], .main .block-container {
    max-width: 100vw !important;
    overflow-x: hidden !important;
    padding-left: 4px !important;
    padding-right: 4px !important;
    padding-top: 1rem !important;
}

/* ★一番の原因：要素間の広すぎる隙間をゼロにする★ */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0px !important; /* ←ここが超重要！隙間を消す */
    width: 100% !important;
}

/* 各列のパディングを極限まで削る */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: 0 !important; 
    padding: 0 2px !important; /* 左右にわずか2pxの余白だけ残す */
}

/* ★各項目の幅を狭くキッチリ固定★ */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { width: 44% !important; flex: 0 0 44% !important; } /* 品名: 広め */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) { width: 17% !important; flex: 0 0 17% !important; } /* 在庫: 狭い */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) { width: 17% !important; flex: 0 0 17% !important; } /* 必要: 狭い */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) { width: 22% !important; flex: 0 0 22% !important; } /* 操作: ボタン用 */

/* ★プルダウン（セレクトボックス）を極限まで小さく★ */
div[data-baseweb="select"] { 
    min-height: 28px !important;
    height: 28px !important;
}
div[data-baseweb="select"] > div {
    padding: 0px 2px !important;
    font-size: 0.75rem !important;
}
.stSelectbox label { display: none !important; }

/* ★ボタンも極限まで小さく★ */
.stButton > button {
    width: 100% !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 !important;
    font-size: 0.7rem !important;
    font-weight: bold !important;
}

/* テキスト類の調整 */
.header-col {
    font-size: 0.7rem;
    color: #888;
    text-align: center !important;
}
.header-left {
    text-align: left !important;
    padding-left: 2px;
}
.item-buy, .item-ok {
    font-size: 0.85rem;
    font-weight: bold;
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important; /* 長い品名ははみ出さずに「...」にする */
    display: block;
}
.item-buy { color: #b7791f; }
.item-ok { color: #333; }

/* 行全体の枠（少し丸みを帯びた背景） */
.item-row {
    padding: 6px 0px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    margin-bottom: 4px;
}
.needs-buy { background-color: #fefcbf; }
.no-buy { background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 4. 品物の追加セクション ---
with st.expander("➕ 品物を追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        col_n, col_c, col_ne = st.columns([44, 17, 17]) # CSSで強制されます
        with col_n:
            name_in = st.text_input("品名", placeholder="例：バナナ", label_visibility="collapsed")
        with col_c:
            curr_in = st.selectbox("在庫", range(16), index=0, label_visibility="collapsed")
        with col_ne:
            need_in = st.selectbox("必要", range(16), index=1, label_visibility="collapsed")
        
        if st.form_submit_button("追加") and name_in:
            add_item(name_in, curr_in, need_in)
            st.rerun()

st.write("") 

# --- 5. 買い物リスト表示 ---
h1, h2, h3, h4 = st.columns([44, 17, 17, 22])
with h1: st.markdown('<div class="header-col header-left">品名</div>', unsafe_allow_html=True)
with h2: st.markdown('<div class="header-col">在庫</div>', unsafe_allow_html=True)
with h3: st.markdown('<div class="header-col">必要</div>', unsafe_allow_html=True)
with h4: st.markdown('<div class="header-col">操作</div>', unsafe_allow_html=True)

items = get_items()

if not items:
    st.info("リストは空です")
else:
    for item in items:
        idx, name, curr, need = item
        is_buying = need > 0
        
        row_class = "needs-buy" if is_buying else "no-buy"
        
        st.markdown(f'<div class="item-row {row_class}">', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns([44, 17, 17, 22])
        
        with c1:
            if is_buying:
                st.markdown(f'<div class="item-buy" title="{name}">🛒 {name}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="item-ok" title="{name}">{name}</div>', unsafe_allow_html=True)
                
        with c2:
            st.selectbox("在庫", range(16), index=curr, key=f"c_{idx}", label_visibility="collapsed", on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            
        with c3:
            st.selectbox("必要", range(16), index=need, key=f"n_{idx}", label_visibility="collapsed", on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            
        with c4:
            if is_buying:
                st.button("購入", key=f"buy_{idx}", type="primary", on_click=buy_item, args=(idx, curr, need))
            else:
                st.button("削除", key=f"del_{idx}", on_click=delete_item_callback, args=(idx,))
                
        st.markdown('</div>', unsafe_allow_html=True)
