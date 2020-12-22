import cv2
import numpy as np
import pandas as pd
import streamlit as st
from gtts import gTTS

st.title('流木解析結果_話しかける')

uploaded_file = st.sidebar.file_uploader("Choose a image file", type="jpg")

if uploaded_file is not None:
    # Convert the file to an opencv image.
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)

    canny_gray = cv2.Canny(opencv_image,100,53)
    cimg = canny_gray

    dp=1
    minDist=42
    param1=100
    param2=15
    minRadius=21
    maxRadius=29
    gazou_waku_xstart=590
    gazou_waku_xend=2390
    gazou_waku_ystart=1070
    gazou_waku_yend=3250
    
    
    circles = cv2.HoughCircles(cimg,
                               cv2.HOUGH_GRADIENT,
                               dp=dp,
                               minDist=minDist,
                               param1=param1,
                               param2=param2,
                               minRadius=minRadius,
                               maxRadius=maxRadius)

    data = circles.reshape(-1,3)
    df = pd.DataFrame(data,columns = ['a','b','c'])
    df = df.query('@gazou_waku_xstart < a < @gazou_waku_xend')
    df = df.query('@gazou_waku_ystart < b < @gazou_waku_yend')
    df = df.values
    data_circles = df.reshape(1,df.shape[0],3)
    
    #検出された際に動くようにする。
    if data_circles is not None and len(data_circles) > 0:
        #型をfloat32からunit16に変更：整数のタイプになるので、後々トラブルが減る。
        circles = np.uint16(np.around(data_circles))
        for i in data_circles[0,:]:
            x=int(i[0])
            y=int(i[1])
            r=int(i[2])
            # 外側の円を描く
            cv2.circle(opencv_image,(x,y),r,(0,255,0),2)
            # 中心の円を描く
            cv2.circle(opencv_image,(x,y),5,(208,22,146),-1)

    honsu = data_circles.shape[1]
    
    mytext = str(honsu) + '本です'
    tts = gTTS(text=mytext, lang='ja')
    tts.save('honsu.mp3')
    audio_file = open(‘honsu.mp3’, ‘rb’)
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format=‘audio/ogg’,start_time=0)
    
    

    cv2.putText(opencv_image,
                str(honsu),
                (200,400),
                cv2.FONT_HERSHEY_SIMPLEX,
                11,
                (208,22,146),
                10)
        

    # Now do something with the image! For example, let's display it:
    st.image(opencv_image, channels="BGR",width=450)
	playsound('./honsu.mp3')
