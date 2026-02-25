import streamlit as st
import sqlite3

# --- 1. データベース処理 (SQLite) ---
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

# --- 2. UI設定 & カスタムCSS ---
st.set_page_config(page_title="買い物リスト", layout="centered")

# スマホ画面でも強制的に横並びを維持し、余白を削る魔法のCSS
st.markdown("""
    <style>
    /* 全体の余白を最小限に */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 0.3rem;
        padding-right: 0.3rem;
    }
    /* st.columns がスマホで縦に並ぶのを防ぐ（横並びを維持） */
    [data-testid="column"] {
        min-width: 0px !important;
        flex-basis: auto !important;
    }
    /* セレクトボックスのラベルを消し、高さを低くする */
    .stSelectbox label {
        display: none !important;
    }
    div[data-baseweb="select"] {
        min-height: 32px !important;
    }
    /* ボタンをコンパクトにする */
    .stButton > button {
        width: 100%;
        padding: 0px 2px;
        font-size: 0.8rem;
        height: 32px;
        line-height: 32px;
    }
    /* 品名のテキスト調整 */
    .item-name {
        font-size: 0.85rem;
        font-weight: bold;
        line-height: 1.2;
        word-break: break-all;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    /* ヘッダーの調整 */
    .header-label {
        font-size: 0.7rem;
        color: #888;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 3. 品物の追加セクション ---
with st.expander("➕ 品物を追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        col_n, col_c, col_ne = st.columns([2.5, 1, 1])
        with col_n:
            name_in = st.text_input("品名", placeholder="例：バナナ")
        with col_c:
            curr_in = st.selectbox("在庫", range(16), index=0)
        with col_ne:
            need_in = st.selectbox("必要", range(16), index=1)
        
        if st.form_submit_button("追加") and name_in:
            add_item(name_in, curr_in, need_in)
            st.rerun()

st.write("") # スペース

# --- 4. 買い物リスト表示 ---
# ヘッダー（スマホでも1行に収まる比率）
# 比率: 品名(3.5) 在庫(1.8) 必要(1.8) ボタン(1.8)
h1, h2, h3, h4 = st.columns([3.5, 1.8, 1.8, 1.8])
with h1: st.markdown('<div class="header-label" style="text-align:left;">品名</div>', unsafe_allow_html=True)
with h2: st.markdown('<div class="header-label">在庫</div>', unsafe_allow_html=True)
with h3: st.markdown('<div class="header-label">必要</div>', unsafe_allow_html=True)
with h4: st.markdown('<div class="header-label">操作</div>', unsafe_allow_html=True)

st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

items = get_items()

if not items:
    st.info("リストは空です")
else:
    for item in items:
        idx, name, curr, need = item
        is_needed = need > 0
        
        # 背景色（必要数が1以上なら薄い黄色）
        bg_color = "#fefcbf" if is_needed else "white"
        
        # アイテム行（1行のまとまり）
        st.markdown(f'<div style="background-color: {bg_color}; padding: 4px; border-radius: 4px; margin-bottom: 2px; border: 1px solid #eee;">', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns([3.5, 1.8, 1.8, 1.8], vertical_alignment="center")
        
        with c1:
            st.markdown(f'<div class="item-name">{name}</div>', unsafe_allow_html=True)
            
        with c2:
            new_c = st.selectbox("在庫", range(16), index=curr, key=f"c_{idx}", label_visibility="collapsed")
            
        with c3:
            new_n = st.selectbox("必要", range(16), index=need, key=f"n_{idx}", label_visibility="collapsed")
            
        # プルダウンの値が変更されたら即時保存
        if new_c != curr or new_n != need:
            update_item_fields(idx, new_c, new_n)
            st.rerun()
            
        with c4:
            if is_needed:
                # 購入ボタン: 「現在の在庫 + 必要数」を在庫へ、必要数は0にする
                if st.button("購入", key=f"buy_{idx}", type="primary"):
                    update_item_fields(idx, min(curr + need, 15), 0)
                    st.rerun()
            else:
                # 削除ボタン
                if st.button("削除", key=f"del_{idx}"):
                    delete_item(idx)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
