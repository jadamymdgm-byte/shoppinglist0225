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

# --- 2. コールバック関数（即時反映の処理） ---
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

# --- 3. UI設定 ---
st.set_page_config(page_title="買い物リスト", layout="centered")

# スマホ向けに画面の余白だけ少しスッキリさせます
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 500px; /* スマホで見やすい幅に制限 */
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 4. 品物の追加セクション（こちらも縦並び） ---
with st.expander("➕ 品物を追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        name_in = st.text_input("品名", placeholder="例：バナナ")
        curr_in = st.selectbox("在庫数", range(16), index=0)
        need_in = st.selectbox("必要数", range(16), index=1)
        
        # ボタンを横幅いっぱいにする
        if st.form_submit_button("リストに追加", use_container_width=True) and name_in:
            add_item(name_in, curr_in, need_in)
            st.rerun()

st.divider()

# --- 5. 買い物リスト表示（縦型カードレイアウト） ---
items = get_items()

if not items:
    st.info("リストは空です")
else:
    for item in items:
        idx, name, curr, need = item
        is_buying = need > 0
        
        # st.container(border=True) で枠線付きのカードを作る
        with st.container(border=True):
            
            # 品名の表示
            st.caption("品名")
            if is_buying:
                st.markdown(f"### 🛒 {name}") # 買うものにはカートマーク
            else:
                st.markdown(f"### {name}")
                
            # 在庫と必要数（標準の縦並び）
            new_c = st.selectbox("在庫数", range(16), index=curr, key=f"c_{idx}", on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            new_n = st.selectbox("必要数", range(16), index=need, key=f"n_{idx}", on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            
            # 操作ボタン
            st.write("") # 少し隙間を空ける
            if is_buying:
                # 購入ボタン（赤系/プライマリーカラーで目立たせる）
                st.button("購入", key=f"buy_{idx}", type="primary", use_container_width=True, on_click=buy_item, args=(idx, curr, need))
            else:
                # 削除ボタン
                st.button("削除", key=f"del_{idx}", use_container_width=True, on_click=delete_item_callback, args=(idx,))
