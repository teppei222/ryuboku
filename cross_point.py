# 交点算出プログラム(関数ver)
# 使い方は、以下でインポートし、データフレームとライン標高を入れるだけ
# from cross_point import cross_point


import pandas

def cross_point(df,h_lines):
    import numpy as np
    import pandas as pd

    np.seterr(divide='ignore')  # 0除算のRuntimeWarningのみを無視扱いとする

    df_cross = df.copy()
    df_final = pd.DataFrame() #最終出力用データフレーム

    df_cross['Z'] = h_lines
    
    x = df_cross['X'].values
    y = df_cross['Y'].values
    z = df_cross['Z'].values


    def find_roots(x,y):
        s = np.abs(np.diff(np.sign(y))).astype(bool)
        return x[:-1][s] + np.diff(x)[s]/(np.abs(y[1:][s]/y[:-1][s])+1)

    d = np.unique(find_roots(x,y-z))

    df_final['X']=d
    df_final['Y']=h_lines

    return df_final
