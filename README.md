# Python Metatrader DataFrame API

for the server side you need to download Metatrader docker from

https://github.com/traderpedroso/datafeed-mt5-docker

## Installation

```
pip install ejtraderMT

or
git clone https://github.com/traderpedroso/ejtraderMT
cd ejtraderMT
python setup.py install

```

### import

```python
from ejtraderMT import Metatrader


```

### Connect to expert to Metatrader 5

```python

# for change the host Metatrader("hostIP")
mt = Metatrader()

```

#### Account information

```python
accountInfo = mt.accountInfo()
print(accountInfo)
print(accountInfo['broker'])
print(accountInfo['balance'])
```

### You can create market or pending order with the commands.

#### Market Orders

```python
# symbol, volume, stoploss, takeprofit, deviation
mt.buy("EURUSD", 0.01, 1.18, 1.19, 5)
mt.sell("EURUSD", 0.01, 1.18, 1.19, 5)
```

#### Limit Orders

```python
# symbol, volume, stoploss, takeprofit, price, deviation
mt.buyLimit("EURUSD", 0.01, 1.17, 1.19, 1.18, 5)
mt.sellLimit("EURUSD", 0.01, 1.20, 1.17, 1.19, 5)
```

#### Stop Orders

```python
#symbol, volume, stoploss, takeprofit, price, deviation
mt.buyStop("EURUSD", 0.01, 1.18, 1.20, 1.19, 5)
mt.sellStop("EURUSD", 0.01, 1.19, 1.17, 1.18, 5)
```

#### Positions & Manipulation

```python
positions = mt.positions()


if 'positions' in positions:
    for position in positions['positions']:
        mt.CloseById(position['id'])


```

#### Orders & Manipulation

```python
orders = mt.orders()

if 'orders' in orders:
    for order in orders['orders']:
        mt.CancelById(order['id'])

```

#### Modify possition

```python
mt.positionModify( id, stoploss, takeprofit)

```

#### Modify order

```python
mt.orderModify( id, stoploss, takeprofit, price)

```

#### close by symbol

```python
mt.CloseBySymbol("EURUSD")

```

#### close particial

```python
# id , volume
mt.ClosePartial( id, volume)

```

#### If you want to cancel all Orders

```python
mt.cancel_all()
```

#### if you want to close all positions

```python
mt.close_all()
```

#### History fromDate toDate

```python
symbol = "EURUSD"
timeframe = "M1"
fromDate = "24/02/2021"
toDate = "24/02/2021"

history = mt.history(symbol,timeframe,fromDate,toDate)
print(history)

                        open     high      low    close  volume  spread
date
2021-02-24 02:55:00  1.21628  1.21637  1.21572  1.21582   228.0       5
2021-02-24 03:00:00  1.21583  1.21620  1.21576  1.21615   273.0       5
2021-02-24 03:05:00  1.21614  1.21618  1.21577  1.21583   338.0       5
2021-02-24 03:10:00  1.21585  1.21608  1.21579  1.21598   218.0       5
2021-02-24 03:15:00  1.21599  1.21603  1.21578  1.21581   199.0       5
2021-02-24 03:20:00  1.21580  1.21608  1.21577  1.21602   323.0       5
2021-02-24 03:25:00  1.21601  1.21606  1.21582  1.21588   157.0       5
2021-02-24 03:30:00  1.21589  1.21597  1.21548  1.21553   238.0       5
2021-02-24 03:35:00  1.21553  1.21578  1.21550  1.21577   216.0       5
2021-02-24 03:40:00  1.21576  1.21579  1.21533  1.21553   242.0       5
2021-02-24 03:45:00  1.21552  1.21554  1.21524  1.21528   245.0       5
2021-02-24 03:50:00  1.21528  1.21543  1.21509  1.21542   198.0       5
2021-02-24 03:55:00  1.21541  1.21557  1.21535  1.21554   214.0       5
2021-02-24 04:00:00  1.21555  1.21567  1.21544  1.21564   222.0       5
2021-02-24 04:05:00  1.21563  1.21564  1.21533  1.21540   207.0       5
2021-02-24 04:10:00  1.21539  1.21559  1.21523  1.21554   206.0       5
2021-02-24 04:15:00  1.21554  1.21566  1.21543  1.21548   244.0       5
2021-02-24 04:20:00  1.21548  1.21564  1.21544  1.21554    99.0       5
2021-02-24 04:25:00  1.21553  1.21565  1.21544  1.21556   149.0       5
2021-02-24 04:30:00  1.21557  1.21563  1.21527  1.21532   133.0       5
2021-02-24 04:35:00  1.21533  1.21558  1.21522  1.21536   184.0       5
2021-02-24 04:40:00  1.21537  1.21550  1.21525  1.21546   260.0       5
2021-02-24 04:45:00  1.21548  1.21548  1.21527  1.21529   216.0       5
2021-02-24 04:50:00  1.21529  1.21547  1.21517  1.21523   151.0       5
2021-02-24 04:55:00  1.21521  1.21527  1.21501  1.21517   160.0       5
2021-02-24 05:00:00  1.21518  1.21521  1.21509  1.21513   130.0       5
2021-02-24 05:05:00  1.21513  1.21516  1.21493  1.21508   202.0       5
2021-02-24 05:10:00  1.21507  1.21520  1.21506  1.21508   129.0       5
2021-02-24 05:15:00  1.21508  1.21515  1.21502  1.21502   129.0       5
2021-02-24 05:20:00  1.21503  1.21506  1.21496  1.21503   120.0       5
2021-02-24 05:25:00  1.21503  1.21513  1.21501  1.21508    64.0       5
2021-02-24 05:30:00  1.21509  1.21513  1.21496  1.21498   134.0       5
2021-02-24 05:35:00  1.21498  1.21503  1.21495  1.21502   101.0       5
2021-02-24 05:40:00  1.21502  1.21504  1.21492  1.21495    89.0       5
2021-02-24 05:45:00  1.21496  1.21498  1.21476  1.21485   123.0       5
2021-02-24 05:50:00  1.21486  1.21496  1.21486  1.21493    41.0       5


```

#### Short History

```python

symbol = "EURUSD"
timeframe = "M1"

history = mt.Shorthistory(symbol,timeframe,1)
print(history)

                        open     high      low    close  volume  spread
date
2021-02-24 02:55:00  1.21628  1.21637  1.21572  1.21582   228.0       5
2021-02-24 03:00:00  1.21583  1.21620  1.21576  1.21615   273.0       5
2021-02-24 03:05:00  1.21614  1.21618  1.21577  1.21583   338.0       5
2021-02-24 03:10:00  1.21585  1.21608  1.21579  1.21598   218.0       5
2021-02-24 03:15:00  1.21599  1.21603  1.21578  1.21581   199.0       5
2021-02-24 03:20:00  1.21580  1.21608  1.21577  1.21602   323.0       5
2021-02-24 03:25:00  1.21601  1.21606  1.21582  1.21588   157.0       5
2021-02-24 03:30:00  1.21589  1.21597  1.21548  1.21553   238.0       5
2021-02-24 03:35:00  1.21553  1.21578  1.21550  1.21577   216.0       5
2021-02-24 03:40:00  1.21576  1.21579  1.21533  1.21553   242.0       5
2021-02-24 03:45:00  1.21552  1.21554  1.21524  1.21528   245.0       5
2021-02-24 03:50:00  1.21528  1.21543  1.21509  1.21542   198.0       5
2021-02-24 03:55:00  1.21541  1.21557  1.21535  1.21554   214.0       5
2021-02-24 04:00:00  1.21555  1.21567  1.21544  1.21564   222.0       5
2021-02-24 04:05:00  1.21563  1.21564  1.21533  1.21540   207.0       5
2021-02-24 04:10:00  1.21539  1.21559  1.21523  1.21554   206.0       5
2021-02-24 04:15:00  1.21554  1.21566  1.21543  1.21548   244.0       5
2021-02-24 04:20:00  1.21548  1.21564  1.21544  1.21554    99.0       5
2021-02-24 04:25:00  1.21553  1.21565  1.21544  1.21556   149.0       5
2021-02-24 04:30:00  1.21557  1.21563  1.21527  1.21532   133.0       5
2021-02-24 04:35:00  1.21533  1.21558  1.21522  1.21536   184.0       5
2021-02-24 04:40:00  1.21537  1.21550  1.21525  1.21546   260.0       5
2021-02-24 04:45:00  1.21548  1.21548  1.21527  1.21529   216.0       5
2021-02-24 04:50:00  1.21529  1.21547  1.21517  1.21523   151.0       5
2021-02-24 04:55:00  1.21521  1.21527  1.21501  1.21517   160.0       5
2021-02-24 05:00:00  1.21518  1.21521  1.21509  1.21513   130.0       5
2021-02-24 05:05:00  1.21513  1.21516  1.21493  1.21508   202.0       5
2021-02-24 05:10:00  1.21507  1.21520  1.21506  1.21508   129.0       5
2021-02-24 05:15:00  1.21508  1.21515  1.21502  1.21502   129.0       5
2021-02-24 05:20:00  1.21503  1.21506  1.21496  1.21503   120.0       5
2021-02-24 05:25:00  1.21503  1.21513  1.21501  1.21508    64.0       5
2021-02-24 05:30:00  1.21509  1.21513  1.21496  1.21498   134.0       5
2021-02-24 05:35:00  1.21498  1.21503  1.21495  1.21502   101.0       5
2021-02-24 05:40:00  1.21502  1.21504  1.21492  1.21495    89.0       5
2021-02-24 05:45:00  1.21496  1.21498  1.21476  1.21485   123.0       5
2021-02-24 05:50:00  1.21486  1.21496  1.21486  1.21493    41.0       5


```

#### Live data and streaming events

```python
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

,,,
### Future add comming soon

```
