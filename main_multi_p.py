import cv2
import numpy as np
import pandas as pd
import streamlit as st
import datetime

dt_now = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=9))
)

st.title('流木解析_複数ボックス用')
st.header('')
st.header(dt_now.strftime('%Y年%m月%d日 %H:%M'))

uploaded_file = st.sidebar.file_uploader("画像ファイルを選択してください。", type="jpg")


xstart = [709,1650,709,1694,709,1633]
xend = [1463,2469,1413,2431,1430,2425]
ystart = [1094,1100,1903,1903,2590,2590]
yend = [1705,1688,2519,2546,3173,3179]
minus = 5


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
    minRadius=18
    maxRadius=26

    
    circles = cv2.HoughCircles(cimg,
                               cv2.HOUGH_GRADIENT,
                               dp=dp,
                               minDist=minDist,
                               param1=param1,
                               param2=param2,
                               minRadius=minRadius,
                               maxRadius=maxRadius)

    data = circles.reshape(-1,3)
    for gazou_waku_xstart,gazou_waku_xend,gazou_waku_ystart, gazou_waku_yend in zip(xstart,xend,ystart,yend):
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
                cv2.circle(opencv_image,(x,y),r,(255,255,255),2)
                # 中心の円を描く
                cv2.circle(opencv_image,(x,y),5,(255,255,255),-1)

        honsu = data_circles.shape[1]

        cv2.putText(opencv_image,
                    str(honsu),
                    (gazou_waku_xstart,gazou_waku_ystart-minus),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    6,
                    (208,22,146),
                    22)
        

    # Now do something with the image! For example, let's display it:
    st.image(opencv_image, channels="BGR",width=450)
