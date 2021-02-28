from ejtraderMT import Metatrader
from threading import Thread




api = Metatrader('192.168.1.101')

symbols = ["EURUSD","GBPUSD","AUDUSD"]
timeframe = "TICK"


# Live data stream subscribe
api.live(symbols,timeframe)




def price():
    connect = api.live_price
    while True:
        price = connect.recv_json()
        print(price)


def event():
    connect = api.live_event
    while True:
        event = connect.recv_json()
        print(event)




t = Thread(target=price, daemon=True)
t.start()

t = Thread(target=event, daemon=True)
t.start()




while True:
    pass