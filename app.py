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

# --- 2. コールバック関数（確実なデータ更新処理） ---
# 【購入ボタンを押した時の処理】
def buy_item(idx, curr, need):
    new_curr = min(curr + need, 15) # 現在の在庫 + 必要数 (最大15)
    update_item_fields(idx, new_curr, 0) # 在庫を更新し、必要数を0にする

# 【プルダウンを変更した時の処理】
def update_qty(idx, curr_key, need_key):
    new_c = st.session_state[curr_key]
    new_n = st.session_state[need_key]
    update_item_fields(idx, new_c, new_n)

# 【削除ボタンを押した時の処理】
def delete_item_callback(idx):
    delete_item(idx)


# --- 3. UI設定 & スマホ用CSS ---
st.set_page_config(page_title="買い物リスト", layout="centered")

st.markdown("""
<style>
/* スマホでのカラム縦積みを防止し、強制的に横並びにする */
@media (max-width: 768px) {
    div[data-testid="column"] {
        min-width: 0 !important;
        flex-basis: auto !important;
    }
}
/* コンテナの無駄な余白を削る */
.main .block-container {
    padding-top: 1rem !important;
    padding-left: 0.2rem !important;
    padding-right: 0.2rem !important;
}
/* プルダウンの高さを抑える */
div[data-baseweb="select"] { min-height: 32px !important; }
div[data-baseweb="select"] > div {
    font-size: 0.9rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}
.stSelectbox label { display: none !important; }

/* ボタンのスタイル */
.stButton > button {
    width: 100% !important;
    height: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    font-size: 0.85rem !important;
    font-weight: bold !important;
}

/* ヘッダーの文字スタイル */
.header-col {
    font-size: 0.75rem;
    color: #888;
    font-weight: bold;
    text-align: center;
}
.header-col.left { text-align: left; }

/* 買うべきアイテム（品名）の強調スタイル */
.item-buy {
    background-color: #fefcbf;
    padding: 8px 4px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.85rem;
    color: #b7791f;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
/* 買わなくていいアイテム（品名）のスタイル */
.item-ok {
    padding: 8px 4px;
    font-size: 0.85rem;
    color: #333;
    font-weight: bold;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 4. 品物の追加セクション ---
with st.expander("➕ 品物を追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        col_n, col_c, col_ne = st.columns([3.5, 1.5, 1.5])
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
# ヘッダー (比率 -> 品名:3, 在庫:1.2, 必要:1.2, 操作:1.6)
h1, h2, h3, h4 = st.columns([3, 1.2, 1.2, 1.6])
with h1: st.markdown('<div class="header-col left">品名</div>', unsafe_allow_html=True)
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
        
        # 区切り線
        st.markdown("<hr style='margin: 4px 0; border: none; border-top: 1px dashed #ddd;'>", unsafe_allow_html=True)
        
        # アイテム行
        c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1.6], vertical_alignment="center")
        
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
