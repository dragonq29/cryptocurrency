import time
import pyupbit
import datetime
import requests
import sys

if len(sys.argv) > 1:
    coinType = sys.argv[1]
else:
    print("put Coin Type in argv")
    exit(1)

access = "access"
secret = "secret"
myToken = 'myToken'

fee = 0.0005 # 업비트 수수료 0.05%

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

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
post_message(myToken,"#upbit", "autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-" + coinType)
        end_time = start_time + datetime.timedelta(days=1)

        # 9:00 < 현재 < #8:59:50
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-" + coinType, 0.5)
            ma15 = get_ma15("KRW-" + coinType)
            current_price = get_current_price("KRW-" + coinType)
            if target_price < current_price and ma15 < current_price:
            # if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-" + coinType, krw * (1-fee))
                    post_message(myToken,"#upbit", coinType + " buy : " +str(buy_result))
        else:
            coin = get_balance(coinType)
            current_price = upbit.get_current_price("KRW-" + coinType)
            if (coin * (1-fee)) > 5000: # 가지고 있는 Coin이 5천원 이상일때 전량 매도
                sell_result = upbit.sell_market_order("KRW-" + coinType, coin * (1-fee))
                post_message(myToken,"#upbit", coinType + " buy : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#upbit", e)
        time.sleep(1)