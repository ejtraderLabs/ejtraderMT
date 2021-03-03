from ejtraderMT import Metatrader
from threading import Thread
from ejtraderDB import DictSQLite
import asyncio
import uvloop


api = Metatrader()

symbols = ["EURUSD","GBPUSD","AUDUSD"]
timeframe = "TICK"
local = 'live'

# Live data stream subscribe
api.live(symbols,timeframe)

q = DictSQLite(name=local)

    


async def price():
    connect = api.live_price
    while True:
        price = connect.recv_json()
        try:
            symbol = price['symbol']
            price = price['data']
            q[symbol] = price
        except KeyError:
            pass
        print(price)

async def event():
    connect = api.live_event
    while True:
        event = connect.recv_json()
        print(event)




active = [["EURUSD"],["GBPUSD"]]
timeframe = "M1"
period = 43200
q = DictSQLite(name="history")
async def main():
    while True:
        for i in active:
            df = api.history(i,timeframe,period)
            print(df,end="\r")
            q[f"{i}"] = df
    
uvloop.install()
asyncio.run(main())






uvloop.install()
asyncio.run(price())
asyncio.run(event())




# {'status': 'CONNECTED', 'symbol': 'GBPUSD', 'timeframe': 'TICK', 'data': [1614723675076, 1.39677, 1.3968]}
# {'status': 'CONNECTED', 'symbol': 'AUDUSD', 'timeframe': 'TICK', 'data': [1614723675076, 1.39677, 1.3968]}