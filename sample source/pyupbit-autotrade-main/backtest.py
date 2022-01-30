from cgitb import text
import tkinter
import pyupbit
import numpy as np
from tkinter import *
from tkinter import messagebox
import datetime


window=tkinter.Tk()
window.geometry('450x500')

# w = Tk()
# w.geometry('450x500')
# w.title('변동성 돌파 전략')
# w.resizable(0, 0)

df = pyupbit.get_ohlcv("KRW-BTC", count=20)
# df = pyupbit.get_ohlcv("KRW-BTC", count=200)
# df = pyupbit.get_ohlcv("KRW-BTC")

def search():
    cnt = 0
    if not count.get():
        cnt = 200
    else:
        cnt = int(count.get())
        
    df = pyupbit.get_ohlcv("KRW-BTC", count=cnt, to=toDate.get())
    
    test(df)
    test_reverse(df)

    print(toDate.get())
    print(count.get())

lb_date = tkinter.Label(window, width=60, text="검사일(2021-01-01)")
# lb_date.place(relx=0.1,rely=0.1,anchor='center')
lb_date.pack()
# lb_date.place(x=20, y=25)

toDate=tkinter.Entry(window, width=20)
toDate.insert(0, datetime.date.today().isoformat())

# toEntry.bind("<Return>", search)
# toEntry.place(x=150, y=20)
toDate.pack()

lb_count = tkinter.Label(window, width=60, text="조회 카운트")
# lb_count.place(x=0, y=125)
lb_count.pack()

count=tkinter.Entry(window, width=20)
count.insert(0, 200)
# count.bind("<Return>", calc)
# count.place(x=150, y=50)
count.pack()

searchCount=tkinter.Label(window)
# toDate.place(x=20,y=80)
searchCount.pack()


button = tkinter.Button(window, text="조회",  width=20, command=search, bg="black")
# button.place(x=20,y=200)
button.pack()

result = tkinter.Label(window, width=60)
result.pack()

result1 = tkinter.Label(window, width=60)
result1.pack()

result2 = tkinter.Label(window, width=60)
result2.pack()

result3 = tkinter.Label(window, width=60)
result3.pack()

# lb_date.insert("current", df.index[0])
# lb_date.insert("current", " ~ ")
# lb_date.insert("current", df.index[-1])
# lb_date.place(x=20, y=20)
# # lb_date.pack()

# lb_date2 = tkinter.Text(window)
# lb_date2.insert(tkinter.CURRENT, "검사일2 : ")
# lb_date2.insert("current", df.index[0])
# lb_date2.insert("current", " ~ ")
# lb_date2.insert("current", df.index[-1])
# lb_date2.place(x=20, y=40)
# # lb_date.pack()


# entry=tkinter.Entry(window)
# entry.bind("<Return>", calc)
# entry.place(x=20, y=40)
# # entry.pack()

# label=tkinter.Label(window)
# label.pack()

# lb_date = Label(w, bg='white')
# lb_date["text"] = "검사일 : ", df.index[0], '~', df.index[-1]
# # lb_date.config(font=1)
# lb_date.place(x=20, y=50)
    
    
    
    
# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
# df = pyupbit.get_ohlcv("KRW-BTC", period=1, to="20211002 00:15:00", interval="minute15", count=192)

def test(df):
    # 변동폭 * k 계산, (고가 - 저가) * k값
    df['range'] = (df['high'] - df['low']) * 0.5

    # target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
    df['target'] = df['open'] + df['range'].shift(1)

    # ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
    df['ror'] = np.where(df['high'] > df['target'],
                        (df['close'] / df['target']) * 0.9994, #사고팔고 합쳐서 수수료 0.01%    //비트겟 수수료 0.03 * 2
                    # (df['close'] / df['target']),
                        1)

    # 누적 곱 계산(cumprod) => 누적 수익률
    df['hpr'] = df['ror'].cumprod()

    # Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

    #MDD 계산
    # print("MDD(%): ", df['dd'].max())

    # 엑셀로 출력
    # print(df)
    #((100/150)-1)*100
    #((매도가/매수가) - 1) * 100 = 수익률

    date = df.index[0], '~', df.index[-1]
    print('date', date)
    # print('시작일 : ', df.iloc[0]['index'], '종료일 : ', df.iloc[-1]['index'])'

    # label=tkinter.Label(w, text=df.index[0])
    # label.config(font=1)
    # label.insert("current", "1")
    # label.place(x=20, y=50)

    # label=tkinter.Label(window, text="파이썬")
    # label.place(x=20,y=20)
    # label.pack()
    
    # def calc(event):
    #     toDate.config(text="기간 : " + entry.get())
    #     # label.config(text="결과="+str(eval(entry.get())))

    
    longVal = round(((df.iloc[-1]['hpr'] - 1) * 100), 2)
                    
    coin = (round((((df.iloc[-1]['close']/df.iloc[0]['open']) - 1) * 100), 2),'%')
    long = (round(((df.iloc[-1]['hpr'] - 1) * 100), 2), '%')
    result['text'] = "coin : ", coin
    result1['text'] = "long : ", long
    
    # result1['text'] = ("long:", str1)
    
    print('coin : ', coin)
    print('long : ', long)

    lb_date.config(text=date)

def test_reverse(df):
    # 변동폭 * k 계산, (고가 - 저가) * k값
    df['range'] = (df['high'] - df['low']) * 0.7

    # target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
    df['target'] = df['open'] - df['range'].shift(1)

    # ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
    df['ror'] = np.where(df['low'] < df['target'],
                        ((df['target'] / df['close']) * 0.9994), #사고팔고 합쳐서 수수료 0.01%
                    # (df['close'] / df['target']),
                        1)

    # 누적 곱 계산(cumprod) => 누적 수익률
    df['hpr'] = df['ror'].cumprod()

    # Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

    #MDD 계산
    # print("MDD(%): ", df['dd'].max())

    #엑셀로 출력
    # print(df)
    #((100/150)-1)*100
    #((매도가/매수가) - 1) * 100 = 수익률

    # print('\n숏', df.index[0], '~', df.index[-1])
    date = df.index[0], '~', df.index[-1]
    # print('시작일 : ', df.iloc[0]['index'], '종료일 : ', df.iloc[-1]['index'])'
    # lb_date = Label(w, bg='white')
    # lb_date["text"] = "검사일 : ", df.index[0], '~', df.index[-1]
    # # lb_date.config(font=1)
    # lb_date.place(x=20, y=50)

    shortVal = round(((df.iloc[-1]['hpr'] - 1) * 100), 2)
    short = (round(((df.iloc[-1]['hpr'] - 1) * 100), 2), '%')
    # print('코인 등락폭 : ', round((((df.iloc[-1]['close']/df.iloc[0]['open']) - 1) * 100), 2),'%')
    print('short : ', short)
    
    result2['text'] = "short : ", short

    # result3['text'] = "sum : ", longVal + shortVal


# df.to_excel("dd.xlsx")


test(df)
test_reverse(df)

window.mainloop()


