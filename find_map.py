import pandas as pd
import streamlit as st

df_header = pd.read_csv('./DB2.csv',encoding="cp932")
df = df_header.set_index('ID')

kani = df["流域"].unique().tolist()
container_a = st.sidebar.beta_container()
all_a = st.sidebar.checkbox("すべて選択",key="1")
if all_a:
    selected_options_kani = container_a.multiselect("流域を選んでください:",kani,kani)
else:
    selected_options_kani =  container_a.multiselect("流域を選んでください:",kani)
df = df[df['流域'].isin(selected_options_kani)]


basho = df["型式"].unique().tolist()
container_b = st.sidebar.beta_container()
all_b = st.sidebar.checkbox("すべて選択",key="2")
if all_b:
    selected_options_basho = container_b.multiselect("型式を選んでください:",basho,basho)
else:
    selected_options_basho =  container_b.multiselect("型式を選んでください:",basho)
df = df[df['型式'].isin(selected_options_basho)]
st.header('該当施設検索')
st.map(df)
st.table(df)