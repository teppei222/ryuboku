import streamlit as st

if "login" not in st.session_state:
    st.session_state["login"] = False

pw_dict = {
    "山田たかし": "yt",
    "田所剛": "tt",
}

if st.session_state["login"] == False:
    name = st.text_input("ユーザー名を漢字で入力(空白なし)", placeholder="山田太郎")
    password = st.text_input("パスワードを半角英小文字で入力", placeholder="yt")
    if st.button("ログイン"):
        if pw_dict[name] == password:
            st.session_state["login"] = True
        else:
            raise ValueError("パスワードが違います")
        

if st.session_state["login"] == True:
    test_key = st.secrets["test_file"]["test_api"]
else:
    test_key = "キー取得不可"
st.write(f"API：{test_key}")