import pyupbit
import numpy as np
from tkinter import *
from tkinter import messagebox

# w = Tk()
# w.geometry('350x500')
# w.title('변동성 돌파 전략')
# w.resizable(0, 0)


# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
# df = pyupbit.get_ohlcv("KRW-BTC", period=1, to="20211002 00:15:00", interval="minute15", count=192)
df = pyupbit.get_ohlcv("KRW-BTC", count=100)

# 변동폭 * k 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] - df['range'].shift(1)

# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['low'] < df['target'],
                     ((df['target'] / df['close']) * 0.999), #사고팔고 합쳐서 수수료 0.01%
                    # (df['close'] / df['target']),
                     1)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#MDD 계산
print("MDD(%): ", df['dd'].max())

#엑셀로 출력
print(df)
#((100/150)-1)*100
#((매도가/매수가) - 1) * 100 = 수익률

print(df.index[0], '~', df.index[-1])
date = df.index[0], '~', df.index[-1]
# print('시작일 : ', df.iloc[0]['index'], '종료일 : ', df.iloc[-1]['index'])'
# lb_date = Label(w, bg='white')
# lb_date["text"] = "검사일 : ", df.index[0], '~', df.index[-1]
# # lb_date.config(font=1)
# lb_date.place(x=20, y=50)

print('코인 등락폭 : ', round((((df.iloc[-1]['close']/df.iloc[0]['open']) - 1) * 100), 2),'%')
print('변동성 돌파전략 : ', round(((df.iloc[-1]['hpr'] - 1) * 100), 2), '%')

# df.to_excel("dd.xlsx")




# w.mainloop()
