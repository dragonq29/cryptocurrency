import pyupbit

access = "access"
secret = "secret"
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-MED"))
print(upbit.get_balance("KRW"))