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

# --- 2. UI設定 & スマホ強制横並びCSS ---
st.set_page_config(page_title="買い物リスト", layout="centered")

st.markdown("""
<style>
/* === スマホ画面での「縦並び」を強制解除する魔法のコード === */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        padding: 0 2px !important;
    }
    /* スマホ画面での列の比率を固定 (品名:3.5, 在庫:1.5, 必要:1.5, 操作:2.2) */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { flex: 3.5 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) { flex: 1.5 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) { flex: 1.5 !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) { flex: 2.2 !important; }
}

/* 画面全体の無駄な余白を削る */
.main .block-container {
    padding-top: 1rem !important;
    padding-left: 0.2rem !important;
    padding-right: 0.2rem !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

/* プルダウンのラベルを隠し、高さを低くする */
.stSelectbox label { display: none !important; }
div[data-baseweb="select"] { min-height: 32px !important; }
div[data-baseweb="select"] > div {
    font-size: 0.85rem !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* ボタンをコンパクトにする */
.stButton > button {
    width: 100% !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    font-size: 0.85rem !important;
    font-weight: bold !important;
}

/* 品名テキストの調整 (長すぎる場合は「...」で省略) */
.item-name {
    font-size: 0.85rem;
    font-weight: bold;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ヘッダーの文字スタイル */
.header-col {
    font-size: 0.7rem;
    color: #666;
    font-weight: bold;
    text-align: center;
}
.header-col.left { text-align: left; }

</style>
""", unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 3. 品物の追加セクション ---
with st.expander("➕ 品物を追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        col_n, col_c, col_ne = st.columns([3.5, 1.5, 1.5])
        with col_n:
            name_in = st.text_input("品名", placeholder="例：バナナ", label_visibility="collapsed")
        with col_c:
            curr_in = st.selectbox("在庫", range(16), index=0, key="add_curr", label_visibility="collapsed")
        with col_ne:
            need_in = st.selectbox("必要", range(16), index=1, key="add_need", label_visibility="collapsed")
        
        if st.form_submit_button("追加") and name_in:
            add_item(name_in, curr_in, need_in)
            st.rerun()

st.write("") 

# --- 4. 買い物リスト表示 ---
# ヘッダー作成
h1, h2, h3, h4 = st.columns([3.5, 1.5, 1.5, 2.2])
with h1: st.markdown('<div class="header-col left">品名</div>', unsafe_allow_html=True)
with h2: st.markdown('<div class="header-col">在庫</div>', unsafe_allow_html=True)
with h3: st.markdown('<div class="header-col">必要</div>', unsafe_allow_html=True)
with h4: st.markdown('<div class="header-col">操作</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin: 4px 0 8px 0;'>", unsafe_allow_html=True)

items = get_items()

if not items:
    st.info("リストは空です")
else:
    for item in items:
        idx, name, curr, need = item
        is_needed = need > 0
        
        # 背景色: 買うものがある時は薄い黄色
        bg_color = "#fefcbf" if is_needed else "#ffffff"
        
        # 1行のコンテナ
        st.markdown(f'<div style="background-color: {bg_color}; padding: 4px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 4px;">', unsafe_allow_html=True)
        
        # 列の配置
        c1, c2, c3, c4 = st.columns([3.5, 1.5, 1.5, 2.2], vertical_alignment="center")
        
        with c1:
            # title属性をつけておくと、文字が省略されても長押しで全文字確認できます
            st.markdown(f'<div class="item-name" title="{name}">{name}</div>', unsafe_allow_html=True)
            
        with c2:
            new_c = st.selectbox("在庫", range(16), index=curr, key=f"c_{idx}", label_visibility="collapsed")
            
        with c3:
            new_n = st.selectbox("必要", range(16), index=need, key=f"n_{idx}", label_visibility="collapsed")
            
        # プルダウン操作で即保存
        if new_c != curr or new_n != need:
            update_item_fields(idx, new_c, new_n)
            st.rerun()
            
        with c4:
            if is_needed:
                # 購入ボタン：現在の在庫 ＋ 必要数 を在庫に入れ、必要数を0にする
                if st.button("購入", key=f"buy_{idx}", type="primary"):
                    update_item_fields(idx, min(curr + need, 15), 0)
                    st.rerun()
            else:
                # 削除ボタン
                if st.button("削除", key=f"del_{idx}"):
                    delete_item(idx)
                    st.rerun()
                    
        st.markdown('</div>', unsafe_allow_html=True)
