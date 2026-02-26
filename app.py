import streamlit as st
import sqlite3
import json

# --- 1. データベース処理 (SQLite) ---
def init_db():
    conn = sqlite3.connect('shopping_list_simple.db', check_same_thread=False)
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

# --- 2. コールバック関数 (即時反映用) ---
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
st.set_page_config(page_title="買い物チェックリスト", layout="centered")

st.markdown("""
<style>
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 500px;
}
.stButton > button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 買い物リスト")

# --- 4. 品物の追加セクション ---
with st.expander("➕ 品物を追加する", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        name_in = st.text_input("品名", placeholder="例：バナナ")
        col_1, col_2 = st.columns(2)
        with col_1:
            curr_in = st.selectbox("現在の在庫", range(16), index=0)
        with col_2:
            need_in = st.selectbox("買う必要がある数", range(16), index=1)
        
        if st.form_submit_button("リストに追加", use_container_width=True) and name_in:
            add_item(name_in, curr_in, need_in)
            st.rerun()

st.write("") 

# --- 5. 買い物リスト表示 (縦型カードレイアウト) ---
items = get_items()

if not items:
    st.info("リストは空です。「品物を追加する」から登録してください。")
else:
    for item in items:
        idx, name, curr, need = item
        is_buying = need > 0
        
        with st.container(border=True):
            st.caption("品名")
            if is_buying:
                st.markdown(f"### 🛒 {name}")
            else:
                st.markdown(f"### {name}")
            
            col_curr, col_need = st.columns(2)
            with col_curr:
                st.selectbox("在庫数", range(16), index=curr, key=f"c_{idx}", 
                             on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            with col_need:
                st.selectbox("必要数", range(16), index=need, key=f"n_{idx}", 
                             on_change=update_qty, args=(idx, f"c_{idx}", f"n_{idx}"))
            
            st.write("") 
            if is_buying:
                st.button("購入完了（在庫にプラス）", key=f"buy_{idx}", type="primary", 
                          use_container_width=True, on_click=buy_item, args=(idx, curr, need))
            else:
                st.button("項目を削除", key=f"del_{idx}", 
                          use_container_width=True, on_click=delete_item_callback, args=(idx,))

# --- 6. データのバックアップ/復元セクション ---
st.write("---")
with st.expander("💾 データのバックアップ/復元"):
    st.subheader("現在のバックアップ")
    backup_data = [{"name": i[1], "current": i[2], "needed": i[3]} for i in items]
    st.code(json.dumps(backup_data, ensure_ascii=False), language="json")
    st.caption("↑ これを長押しでコピーして、メモ帳などに保存してください。")
    
    st.divider()
    
    st.subheader("リストを復元する")
    restore_text = st.text_area("保存していたテキストをここに貼り付けてください", placeholder='[{"name": "バナナ", ...}]')
    if st.button("このデータで復元する", use_container_width=True):
        if restore_text:
            try:
                data = json.loads(restore_text)
                # 既存のデータを全削除（重複防止のため）
                c = conn.cursor()
                c.execute("DELETE FROM items")
                # データを流し込む
                for d in data:
                    add_item(d['name'], d['current'], d['needed'])
                st.success("復元が完了しました！")
                st.rerun()
            except Exception as e:
                st.error("エラー：正しい形式のデータではありません。")
