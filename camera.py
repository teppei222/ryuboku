import streamlit as st

st.write("表題やテキスト")
picture = st.camera_input("Take a picture")

if picture:
     st.image(picture)
