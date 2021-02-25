from ejtraderMT import Metatrader
from threading import Thread




api = Metatrader()

symbols = ["EURUSD","GBPUSD","AUDUSD"]
timeframe = "TICK"


# Live data stream subscribe
api.live(symbols,timeframe)




def price():
    connect = api.livePrice
    while True:
        price = connect.recv_json()
        print(price)


def event():
    connect = api.liveEvent
    while True:
        event = connect.recv_json()
        print(event)




t = Thread(target=price, daemon=True)
t.start()

t = Thread(target=event, daemon=True)
t.start()




while True:
    pass