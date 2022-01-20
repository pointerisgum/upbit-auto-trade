import time
import pyupbit
import datetime
import requests
import schedule
from fbprophet import Prophet
import upbit_api

access = "xwdEMciw0PeGRfpA8xMaVtnVGmFPFxTR6dkKCnUQ"
secret = "UOxwdGYVZflyTCbMwrlrzB0Ey44GGxSLl70xp8A4"
slackToken = "xoxb-2958422443234-2961015128436-OlEZV7qGyaamz31X3slydehR"

buyTicker = ""
target_price = ""
k = 0.5

# data = upbit_api.get_candle("KRW-BTC", "1", 100)
# print(upbit_api.get_rsi(data))

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    print("===AI 종가 예측 업데이트===")
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
    
# if len(target_price) > 0:
#     predict_price(target_price)
#     schedule.every().hour.do(lambda: predict_price(target_price))

def initTickers():
    print("initTickersinitTickersinitTickersinitTickersinitTickers")
    global tickers
    tickers = ["KRW-BTC", "KRW-ETH", "KRW-BCH", "KRW-AAVE", "KRW-LTC", "KRW-SOL", "KRW-BSV", "KRW-AXS", "KRW-ATOM", "KRW-BTG",
               "KRW-STRK", "KRW-ETC", "KRW-DOT", "KRW-NEO", "KRW-LINK", "KRW-NEAR", "KRW-REP", "KRW-WAVES", "KRW-QTUM", "KRW-FLOW",
               "KRW-OMG", "KRW-WEMIX", "KRW-KAVA", "KRW-GAS", "KRW-SBD", "KRW-TON", "KRW-SAND", "KRW-XTZ", "KRW-THETA", "KRW-AQT"]  #알파쿼크까지 총 30개

initTickers()
        
#현재가가 큰 순으로 변동성이 있는 코인을 가져온다
def get_target_ticker(k):
    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        current_price = get_current_price(ticker)
        if target_price < current_price:
            # print("predicted_close_price : ", predicted_close_price)
            predict_price(ticker)
            return ticker
            # if predicted_close_price == 0:
            #     print("AI 예측 결과 스케쥴 등록")
            #     predict_price(ticker)
            # return ticker
    return ""

#매 시간마다 티커들 리셋해줌
schedule.every().hour.do(lambda: initTickers())


# schedule.every().hour.do(lambda: predict_price(target_price))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 시작 메세지 슬랙 전송
post_message(slackToken,"#stock", "프로그램 시작")


while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()
   
        if start_time < now < end_time - datetime.timedelta(seconds=30):
            if len(buyTicker) > 0:
                print("오늘 이미 구매한 코인이 있음")
                time.sleep(1)
                continue
            
            target_ticker = get_target_ticker(k)
            if len(target_ticker) > 0:
            # if target_ticker.length() > 0:
                print("조건에 만족하는 타겟티커:", target_ticker)
                target_price = get_target_price(target_ticker, k)
                current_price = get_current_price(target_ticker)
                # ma15 = get_ma15(target_ticker)
            
                print("현재 금액 : ", current_price)
                print("마감 예상 금액 : ", predicted_close_price)
                
                # if ma15 >= current_price:
                #     print("15일 이평선을 만족하지 못하여 구매하지 않음")
                #     tickers.remove(target_ticker)
                if current_price >= predicted_close_price:
                    print("AI가 분석한 결과 종가가 현재가보다 작을 것으로 예상 되어 구매하지 않음")
                    tickers.remove(target_ticker)
                else:
                    krw = get_balance("KRW")
                    if krw > 5000:
                        # buy_result = upbit.buy_market_order(target_ticker, krw*0.9995)
                        buy_result = upbit.buy_market_order(target_ticker, 5500*0.9995)    #테스트용으로 만원어치만 삼
                        buyTicker = target_ticker
                        post_message(slackToken, "#stock", "buy : " +str(buy_result))
                        print(buyTicker, "구매성공")
            else:
                print("조건에 만족하는 티커 없음")
        else:
            if len(buyTicker) > 0:
            # if buyTicker.length() > 0:
                current_btc_price = get_current_price(buyTicker)
                print(current_btc_price)
                balance_name = buyTicker.replace("KRW-", "")
                print("balance:", balance_name)
                balance = get_balance(balance_name)
                # btc = get_balance("BTC")
                # if btc > 0.00008:
                # if btc > (7000/current_btc_price):
                sell_result = upbit.sell_market_order(buyTicker, balance*0.9995)
                buyTicker = ""
                post_message(slackToken, "#stock", "sell : " +str(sell_result))
                initTickers()
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(slackToken, "#stock", e)
        time.sleep(1)
#test1