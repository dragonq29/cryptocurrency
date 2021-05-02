import pyupbit
import numpy as np

# https://youtu.be/5vofEMqMyGk 참고

#OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에대한 데이터
df = pyupbit.get_ohlcv("KRW-BTC", count=7)

# 변동성 돌파 기준 번위 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5

# range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

# 수수료
fee = 0.0

# ror(수익율), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee,
                     1)

# hpr(누적 곱) 계산 (cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# dd:Draw Down(하락폭) 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#MDD 계산 (dd중에 최대값)
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")