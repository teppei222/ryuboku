import plotly.graph_objs as go
import plotly.offline as offline
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from cross_point import cross_point
import io
import base64
import os
import json
import pickle
import uuid
import re
import scipy.optimize as opt
from PIL import ImageGrab
import time

st.set_page_config(layout='wide')

col1, col2 = st.beta_columns(2)

with col1:

    #streamlitでボタンでファイル選択するための構文
    xy_xlsx = st.file_uploader("Choose a Excel file", type="xlsx")

    if xy_xlsx is not None:
        #断面名取得用プログラム
        xlsx_data = pd.read_excel(xy_xlsx)      
        list_danmen = xlsx_data.columns
        list_danmen = list_danmen[::2].values.tolist()
        option = st.selectbox(
            '必要な断面を選択してください',
            list_danmen)
        st.write('選択された断面は:', option)
        start = list_danmen.index(option)*2
        end = start+1
        df = xlsx_data.iloc[:,start:end+1]
        df.columns = ['X','Y']
        dfa = df.copy().dropna(how='all')

        def PolyArea(x,y):
            return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
        
        #左右のスライダ数値作り
        oudan = st.slider('横断を選択する範囲を決めて',dfa['X'].min(), dfa['X'].max(), (dfa['X'].min(), dfa['X'].max()),step=0.01)
        df_oudan = dfa[(dfa['X'] >= oudan[0]) & (dfa['X'] <= oudan[1])]


        #最深河床からいくつ上げるのかを記載
        df2 = df_oudan.copy()
        title = float(st.text_input('上幅の高さ', '0'))
        river_min = df2['Y'].min()+title

       #上幅の左右を出力
        upper_cross = cross_point(df2,river_min)


        # 面積取得のための先頭座標(閉じた図形にするため)
        start_daikei = upper_cross.head(1)

        # 当初の横断断面積
        area_p = df2[df2['Y'] < river_min].copy()
        df_area = pd.concat([area_p,upper_cross]).sort_values('X',ascending=True)
        df_area = pd.concat([df_area,start_daikei])


        # 底の数値作り
        df3 = df2.copy()
        under_line = df3['Y'].min()
        # under_line = st.slider("底",df3['Y'].min(), df3['Y'].max(), (df2['Y'].min()))
        # under_cross = cross_point(df3,under_line)


        #最適化問題
        high = river_min-under_line
        area = PolyArea(df_area['X'],df_area['Y'])
        joutei = upper_cross['X'].max()-upper_cross['X'].min()

        def func(x):
            return abs (area - (joutei + x)*high*0.5)
        x = opt.minimize_scalar(func, method='brent')

        hanpa = (joutei - x.x)/2
        opti = upper_cross.copy()
        opti.iloc[0,0] =opti.iloc[0,0] +hanpa
        opti.iloc[-1,0]=opti.iloc[-1,0]-hanpa
        opti['Y']=under_line
        saitekika = pd.concat([upper_cross,opti]).sort_values('X',ascending=True)
        saitekika = pd.concat([saitekika,start_daikei])

        st.write("最深河床"+ str(round(under_line,2))+'m')
        st.write('上幅標高：' + str(river_min) +' m')
        st.write("上幅" + str(round(joutei,2))+'m')
        st.write("高さ" + str(round(high,2))+'m')
        st.write("面積" + str(round(area,2))+'m2')
        st.write("最適化した下幅"+str(round(x.x,2))+'m')

        river_shogen = []
        river_shogen.append(option)
        river_shogen.append(under_line)
        river_shogen.append(river_min)
        river_shogen.append(joutei)
        river_shogen.append(high)
        river_shogen.append(area)
        river_shogen.append(x.x) 
        river_shogen_df = pd.DataFrame([river_shogen],columns=['No','最深河床高','上幅標高','上幅','高さ','面積','最適化した下幅'])
        

with col2:
    if xy_xlsx is not None:
        st.write('下の二つが同一にならない場合は、横断の切断位置が変な場所になっている。')
        st.write('断面積：' + str(round(PolyArea(df_area['X'],df_area['Y']),2))+'m2')
        st.write('計算面積：'+str(round(PolyArea(saitekika['X'],saitekika['Y']),2))+'m2')
    

        fig1 = px.line(df,x='X', y='Y',color_discrete_sequence=["blue"])
        fig2 = px.scatter(df2,x='X', y='Y',color_discrete_sequence=["red"])
        fig5 = px.line(saitekika,x='X', y='Y',color_discrete_sequence=["black"])
        fig = go.Figure(data=fig1.data + fig2.data+ fig5.data)


        selected_points = plotly_events(
            fig,
            click_event = False,
            select_event = False,
            override_height = 450,
            override_width = "100%",
                    )
        def download_button(object_to_download, download_filename, button_text, pickle_it=False):
                    """
                    Generates a link to download the given object_to_download.
                    Params:
                    ------
                    object_to_download:  The object to be downloaded.
                    download_filename (str): filename and extension of file. e.g. mydata.csv,
                    some_txt_output.txt download_link_text (str): Text to display for download
                    link.
                    button_text (str): Text to display on download button (e.g. 'click here to download file')
                    pickle_it (bool): If True, pickle file.
                    Returns:
                    -------
                    (str): the anchor tag to download object_to_download
                    Examples:
                    --------
                    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
                    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
                    """
                    if pickle_it:
                        try:
                            object_to_download = pickle.dumps(object_to_download)
                        except pickle.PicklingError as e:
                            st.write(e)
                            return None

                    else:
                        if isinstance(object_to_download, bytes):
                            pass

                        elif isinstance(object_to_download, pd.DataFrame):
                            object_to_download = object_to_download.to_csv(index=False)
                            towrite = io.BytesIO()
                            #object_to_download = object_to_download.to_excel(towrite, encoding='utf-8', index=False, header=True)
                            towrite.seek(0)

                        # Try JSON encode for everything else
                        else:
                            object_to_download = json.dumps(object_to_download)

                    try:
                        # some strings <-> bytes conversions necessary here
                        b64 = base64.b64encode(object_to_download.encode()).decode()

                    except AttributeError as e:
                        b64 = base64.b64encode(towrite.read()).decode()

                    button_uuid = str(uuid.uuid4()).replace('-', '')
                    button_id = re.sub('\d+', '', button_uuid)

                    custom_css = f""" 
                        <style>
                            #{button_id} {{
                                display: inline-flex;
                                align-items: center;
                                justify-content: center;
                                background-color: rgb(255, 255, 255);
                                color: rgb(38, 39, 48);
                                padding: .25rem .75rem;
                                position: relative;
                                text-decoration: none;
                                border-radius: 4px;
                                border-width: 1px;
                                border-style: solid;
                                border-color: rgb(230, 234, 241);
                                border-image: initial;
                            }} 
                            #{button_id}:hover {{
                                border-color: rgb(246, 51, 102);
                                color: rgb(246, 51, 102);
                            }}
                            #{button_id}:active {{
                                box-shadow: none;
                                background-color: rgb(246, 51, 102);
                                color: white;
                                }}
                        </style> """

                    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

                    return dl_link
        saitekika = saitekika.sort_values('X',ascending=True)
        columns = [str(option) + '_X',str(option) + '_Y']
        saitekika.columns =  columns
        filename = 'daikei_XY_'+str(option) + '.csv'
        filename_shogen = 'daikei_shogen_'+str(option) + '.csv'
        filename_image = str(option)+'daikei.png'


        answer = st.button('スクリーンキャプチャ')
        if answer == True:
            time.sleep(1)
            ImageGrab.grab().save('./image/' + filename_image)
            st.write('キャプチャ終了')
        else:
            pass

        con_data = saitekika
        con_data = con_data.drop_duplicates()
        download_button_str = download_button(con_data, filename, f'ここを押すと台形の座標がダウンロードされるよ', pickle_it=False)
        download_button_str_shogen = download_button(river_shogen_df, filename_shogen, f'ここを押すと台形の諸元がダウンロードされるよ', pickle_it=False)
        st.markdown(download_button_str, unsafe_allow_html=True)
        st.markdown(download_button_str_shogen, unsafe_allow_html=True)
