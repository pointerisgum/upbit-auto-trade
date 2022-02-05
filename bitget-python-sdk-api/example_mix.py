import bitget.mix.market_api as market
import bitget.mix.account_api as accounts
import bitget.mix.position_api as position
import bitget.mix.order_api as order
import bitget.mix.plan_api as plan
import bitget.mix.trace_api as trace
import json
import time
import datetime
import datetime as pydatetime
import pandas as pd
import telegram


import logging
import requests
import jwt
import uuid
import hashlib
import math
import os
import pandas as pd
import numpy
 
from urllib.parse import urlencode
from decimal import Decimal


def get_cci(candle_data, loop_cnt):
    try:
 
        # CCI 데이터 리턴용
        cci_list = []
 
        # 오름차순 정렬
        for i in range(0, len(candle_data)):
            candle_data[i][0] = float(candle_data[i][0])
            candle_data[i][1] = float(candle_data[i][1])
            candle_data[i][2] = float(candle_data[i][2])
            candle_data[i][3] = float(candle_data[i][3])
            candle_data[i][4] = float(candle_data[i][4])
            
        ordered_df = pd.DataFrame(candle_data)

        # 계산식 : (Typical Price - Simple Moving Average) / (0.015 * Mean absolute Deviation)
        ordered_df['TP'] = (ordered_df[2] + ordered_df[3] + ordered_df[4]) / 3
        ordered_df['SMA'] = ordered_df['TP'].rolling(window=7).mean()
        ordered_df['MAD'] = ordered_df['TP'].rolling(window=7).apply(lambda x: pd.Series(x).mad())
        ordered_df['CCI'] = (ordered_df['TP'] - ordered_df['SMA']) / (0.015 * ordered_df['MAD'])
 
        # 개수만큼 조립
        for i in range(0, loop_cnt):            
            cci_list.append({"type": "CCI", "DT": ordered_df[0].loc[i], "CCI": round(ordered_df['CCI'].loc[i], 4)})
 
        return cci_list
 
    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

if __name__ == '__main__':
    api_key = "bg_e34e157d2931026fd97d6b78f6980dd2"
    secret_key = "7a7aef9dee5a9aef14fbc5eacd3159615c7c9179d92e90a6043b14da9f74467c"
    passphrase = "bitget_auto"
    teleToken = "5225100528:AAGL0OC4m40gsMkB9haFGm0weJMUSKGqY2U"
    bot = telegram.Bot(token=teleToken)
    isGold = False
    isDead = False
    
    symbol = 'BTCUSDT_UMCBL'

    marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    while True:
        endTime = int(pydatetime.datetime.now().timestamp())

        # print(result)
            # time.sleep(0.3)

        # result = marketApi.tickers('umcbl') #COIN 선물
        # print(result)
        
        
        result = marketApi.candles(symbol, granularity=900,startTime=(endTime * 1000) - (900000*200), endTime=endTime * 1000) #15분봉 200개
        cci_data = get_cci(result, 100)
        cci = cci_data[-1]['CCI']
        print('cci: ', cci)
        
        if len(result) > 0:
            df = pd.DataFrame(result)
            df=df[4].iloc[::1] #4번째가 종가임
            
            ma10 = df.rolling(window=10).mean()
            ma30 = df.rolling(window=30).mean()
            print(ma10.iloc[-2])
            print(ma30.iloc[-2])
            line10 = ma10.iloc[-2] - ma30.iloc[-2]
            line30 = ma10.iloc[-1] - ma30.iloc[-1]
            
            if line10 < 0 and line30 > 0 and isGold == False:
                msg = pydatetime.datetime.now().timestamp(), 'bitget BTC golden cross'
                bot.sendMessage(chat_id="-796323955", text=msg)
                print(pydatetime.datetime.now().timestamp(), 'golden cross')
                isGold = True
                isDead = False
                
                
            if line10 > 0 and line30 < 0 and isDead == False:
                msg = pydatetime.datetime.now().timestamp(), 'bitget BTC dead cross'
                bot.sendMessage(chat_id="-796323955", text=msg)
                print(pydatetime.datetime.now().timestamp(), 'dead croos')
                isGold = False
                isDead = True
            
        time.sleep(1)


    
    
    
    
    
    
    
    
    
    
    result = marketApi.contracts('umcbl')   #USDT 선물 (우리가 쓸 거)
    print(result)

    result = marketApi.depth(symbol, limit=100)
    print(result)

    result = marketApi.ticker(symbol)
    print(result)

    result = marketApi.tickers('dmcbl') #COIN 선물
    print(result)

    result = marketApi.fills(symbol, limit=50)
    print(result)

    result = marketApi.candles(symbol, granularity=900,startTime=1643874599000, endTime=1627544102000)
    print(result)

    result = marketApi.index(symbol)
    print(result)

    result = marketApi.funding_time(symbol)
    print(result)

    result = marketApi.market_price(symbol)
    print(result)

    result = marketApi.history_fund_rate(symbol,pageSize=20,pageNo=1, nextPage=False)
    print(result)

    result = marketApi.current_fund_rate(symbol)
    print(result)

    result = marketApi.open_interest(symbol)
    print(result)

    accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    # result = accountApi.account(symbol, marginCoin='USDT')
    # print(result)

    # result = accountApi.leverage(symbol, marginCoin='USDT', leverage=20, holdSide='long')
    # print(result)

    # result = accountApi.margin(symbol, marginCoin='USDT', amount=20, holdSide='long')
    # print(result)

    # result = accountApi.margin_mode(symbol, marginCoin='USDT', marginMode='crossed')
    # print(result)

    # result = accountApi.position_mode(symbol, marginCoin='USDT', holdMode='double_hold')
    # print(result)

    # result = accountApi.open_count(symbol, marginCoin='USDT', openPrice='3000', openAmount='500', leverage=20)
    # print(result)

    # result = accountApi.accounts('umcbl')
    # print(result)

    positionApi = position.PositionApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    # result = positionApi.single_position(symbol, marginCoin='USDT', holdSide='long')
    # print(result)

    # result = positionApi.all_position(productType='mix_type')
    # print(result)

    orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
    # 804554549183000576
    # result = orderApi.place_order(symbol, marginCoin='USDT', size=1,side='open_short', orderType='limit', price='39723', timeInForceValue='normal')
    # print(result)

    # order_data=[{"price":"38723","size":"1","side":"open_short","orderType":"limit","timeInForceValue":"normal"}, {"price":"25723","size":"1","side":"open_long","orderType":"limit","timeInForceValue":"normal"}]
    # result = orderApi.batch_orders(symbol, marginCoin='USDT', order_data=order_data)
    # print(result)

    # result = orderApi.cancel_orders(symbol, marginCoin='USDT', orderId='804554549183000576')
    # print(result)

    # result = orderApi.cancel_batch_orders(symbol, marginCoin='USDT', orderIds=['804557496038076416','804557496121962497'])
    # print(result)

    # result = orderApi.detail(symbol, orderId='804557496038076416')
    # print(result)

    # result = orderApi.current(symbol)
    # print(result)

    # result = orderApi.history(symbol, startTime='1627454102000', endTime='1627547623000', pageSize=20, lastEndId='',isPre=False)
    # print(result)

    # result = orderApi.fills(symbol, orderId='804553570245029890')
    # print(result)

    planApi = plan.PlanApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    # result = planApi.place_plan(symbol, marginCoin='USDT', size='1', side='open_long', orderType='limit', triggerPrice='39782', executePrice='38982', triggerType='fill_price', timeInForceValue='normal')
    # print(result)

    # result = planApi.modify_plan(symbol, marginCoin='USDT', orderId='804602672390836225', orderType='limit', triggerPrice='39782', executePrice='37222', triggerType='fill_price')
    # print(result)

    # result = planApi.modify_plan_preset(symbol, marginCoin='USDT', orderId='804602672390836225', planType='normal_plan', presetTakeProfitPrice='45000', presetStopLossPrice='34678')
    # print(result)

    # result = planApi.modify_tpsl_plan(symbol, marginCoin='USDT', orderId='804602672390836225', planType='normal_plan', triggerPrice='45000')
    # print(result)

    # result = planApi.place_tpsl(symbol, marginCoin='USDT', planType='normal_plan', triggerPrice='45000', holdSide='open_long')
    # print(result)

    # result = planApi.cancel_plan(symbol, marginCoin='USDT', orderId='804600814695845888', planType='normal_plan')
    # print(result)

    # result = planApi.current_plan(symbol, isPlan='plan')
    # print(result)

    # result = planApi.history_plan(symbol, startTime='1627454102000', endTime='1627558127000', pageSize=20, lastEndId='', isPlan='plan')
    # print(result)

    traceApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

    # traceApi.follower_history_orders('10', '1', '1635782400000', '1635852263953')

    # traceApi.wait_profit_detail("10","1")
