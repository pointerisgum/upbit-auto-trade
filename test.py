import pyupbit
from fbprophet import Prophet

access = "xwdEMciw0PeGRfpA8xMaVtnVGmFPFxTR6dkKCnUQ"
secret = "UOxwdGYVZflyTCbMwrlrzB0Ey44GGxSLl70xp8A4"

upbit = pyupbit.Upbit(access, secret)

buyTicker = "KRW-THETA"

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

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
    # sell_result = upbit.sell_market_order(buyTicker, balance*0.9995)
    sell_result = upbit.sell_market_order(buyTicker, balance)
    buyTicker = ""
    print("success sell")
