import streamlit as st
import sqlite3

# --- 1. データベース処理 (SQLite) ---
def init_db():
    # データベースファイルを作成し、テーブルを準備します
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
st.set_page_config(page_title="買い物チェックリスト", layout="centered")

# ヘッダー固定とデザイン調整用のCSS
st.markdown("""
    <style>
    /* リストのヘッダーを上部に固定 */
    [data-testid="stVerticalBlock"] > div:nth-child(5) {
        position: sticky;
        top: 2.8rem;
        background-color: white;
        z-index: 99;
        padding: 10px 0;
        border-bottom: 2px solid #eee;
    }
    /* ボタンの横幅をいっぱいに広げる */
    .stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 買い物チェックリスト")

# --- 3. 品物の追加セクション ---
with st.expander("➕ 新しい品物を追加", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        col_name, col_curr, col_need = st.columns([3, 1, 1])
        with col_name:
            name_input = st.text_input("品名", placeholder="例：牛乳")
        with col_curr:
            curr_input = st.selectbox("在庫", range(16), index=0)
        with col_need:
            need_input = st.selectbox("必要", range(16), index=1)
        
        submit = st.form_submit_button("リストに追加")
        if submit and name_input:
            add_item(name_input, curr_input, need_input)
            st.rerun()

st.divider()

# --- 4. 買い物リスト表示 ---
st.subheader("現在のリスト")

# 固定ヘッダー
h1, h2, h3, h4 = st.columns([3, 1, 1, 1.5])
h1.markdown("**品名**")
h2.markdown("**在庫**")
h3.markdown("**必要**")
h4.markdown("**操作**")

items = get_items()

if not items:
    st.info("リストにアイテムがありません。上のボタンから追加してください。")
else:
    for item in items:
        idx, name, curr, need = item
        
        # 必要数が1以上の場合は黄色でハイライト
        is_needed = need > 0
        bg_style = "background-color: #fefcbf; border-radius: 8px; padding: 5px; margin-bottom: 5px;" if is_needed else ""
        
        st.markdown(f'<div style="{bg_style}">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1.5], vertical_alignment="center")
        
        with c1:
            st.write(f"**{name}**")
        
        with c2:
            # 在庫数の変更
            new_curr = st.selectbox("在庫", range(16), index=curr, key=f"c_{idx}", label_visibility="collapsed")
        
        with c3:
            # 必要数の変更
            new_need = st.selectbox("必要", range(16), index=need, key=f"n_{idx}", label_visibility="collapsed")
        
        # 数量が手動で変更された場合に即座にDBを更新
        if new_curr != curr or new_need != need:
            update_item_fields(idx, new_curr, new_need)
            st.rerun()
            
        with c4:
            if is_needed:
                # 購入ボタン: 在庫に必要数を足して、必要数を0にする
                if st.button("購入", key=f"buy_{idx}", type="primary"):
                    update_item_fields(idx, min(curr + need, 15), 0)
                    st.rerun()
            else:
                # 削除ボタン
                if st.button("削除", key=f"del_{idx}"):
                    delete_item(idx)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

