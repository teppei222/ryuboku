import pandas as pd
import streamlit as st
import pydeck as pdk
import streamlit.components.v1 as components
import numpy as np

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

name = df["堰堤名"].unique().tolist()
container_c = st.sidebar.beta_container()
selected_options_name = container_c.multiselect("堰堤名を選んでください:",name)
df = df[df['name'].isin(selected_options_name)]


st.header('該当施設検索')
st.write(df)

midpoint = (np.average(df['lon']), np.average(df['lat']))

tooltip = {
    "html": "{堰堤名}",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "1000"},
}

layer = pdk.Layer(
    'ScatterplotLayer',
    df,
    get_position=['lon','lat'],
    auto_highlight=True,
    get_radius='2500',
    get_fill_color='[160, 0, 200, 140]',
    pickable=True)

view_state = pdk.ViewState(
    longitude=midpoint[0],
    latitude=midpoint[1],
    zoom=7,
    min_zoom=3,
    max_zoom=15,
    pitch=0,
    bearing=0)

r = pdk.Deck(map_style ="road", layers=layer, initial_view_state=view_state,tooltip = tooltip)
deck_map = r.to_html(as_string=True)
st.components.v1.html(deck_map,width=800, height=600) 
