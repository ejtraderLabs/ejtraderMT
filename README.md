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

# to change the host Metatrader("hostIP")
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

# History Dataframe Ready

#### History from Date to Date Dataframe

```python
symbol = "EURUSD"
timeframe = "M1"
fromDate = "24/02/2021"
toDate = "24/02/2021"

history = mt.historyDataframe(symbol,timeframe,fromDate,toDate)
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

#### Short History Dataframe

```python

symbol = "EURUSD"
timeframe = "M1"

history = mt.ShorthistoryDataframe(symbol,timeframe,10)
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

# History multiple symbol merged DataFrame

```python
from ejtraderMT import Metatrader

api = Metatrader()

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"
fromDate = "01/01/2021"
toDate = "10/01/2021"

data = api.historyMultiDataFrame(symbol,symbols,timeframe,fromDate,toDate)

print(data)
   open     high      low    close  volume  spread  OPENGBPUSD  HIGHGBPUSD  LOWGBPUSD  CLOSEGBPUSD  VOLUMEGBPUSD  SPREADGBPUSD  OPENAUDUSD  HIGHAUDUSD  LOWAUDUSD  CLOSEAUDUSD  VOLUMEAUDUSD  SPREADAUDUSD
date
2021-01-03 23:00:00  1.22383  1.22394  1.22362  1.22394    21.0      21     1.36486     1.36486    1.36484      1.36484           2.0           130     0.77006     0.77009    0.76992      0.76995           8.0            74
2021-01-03 23:03:00  1.22375  1.22376  1.22366  1.22368     5.0      29     1.36495     1.36505    1.36480      1.36480           5.0            60     0.77009     0.77014    0.76994      0.76994          10.0            32
2021-01-03 23:04:00  1.22363  1.22363  1.22353  1.22353     2.0      52     1.36490     1.36510    1.36490      1.36491           4.0            31     0.76994     0.77019    0.76972      0.76972           5.0            22
2021-01-03 23:05:00  1.22311  1.22321  1.22294  1.22318    26.0      64     1.36490     1.36491    1.36490      1.36491           2.0            24     0.76974     0.76975    0.76974      0.76975           2.0            84
2021-01-03 23:06:00  1.22317  1.22318  1.22290  1.22293     9.0      66     1.36490     1.36491    1.36480      1.36480          10.0            14     0.76973     0.76992    0.76967      0.76967           5.0            49
...                      ...      ...      ...      ...     ...     ...         ...         ...        ...          ...           ...           ...         ...         ...        ...          ...           ...           ...
2021-01-08 22:55:00  1.22213  1.22227  1.22178  1.22214    58.0       8     1.35609     1.35629    1.35572      1.35628          39.0            10     0.77638     0.77648    0.77620      0.77643          54.0            21
2021-01-08 22:56:00  1.22214  1.22214  1.22162  1.22190   125.0       9     1.35628     1.35672    1.35614      1.35630          52.0            13     0.77641     0.77657    0.77635      0.77640          44.0            20
2021-01-08 22:57:00  1.22189  1.22214  1.22162  1.22193   223.0      10     1.35630     1.35643    1.35561      1.35602          46.0            10     0.77638     0.77667    0.77637      0.77661          45.0            19
2021-01-08 22:58:00  1.22201  1.22206  1.22136  1.22153   251.0      16     1.35619     1.35667    1.35547      1.35587          61.0            19     0.77660     0.77665    0.77657      0.77660          37.0            18
2021-01-08 22:59:00  1.22154  1.22193  1.22133  1.22186   172.0      29     1.35588     1.35619    1.35587      1.35619          18.0           108     0.77661     0.77661    0.77639      0.77647           8.0            19

```

#### Short History multiple symbol merged DataFrame

```python
from ejtraderMT import Metatrader


api = Metatrader()

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"


data = api.ShorthistoryMultiDataFrame(symbol,symbols,timeframe,10)


print(data)

 open     high      low    close  volume  spread  OPENGBPUSD  HIGHGBPUSD  LOWGBPUSD  CLOSEGBPUSD  VOLUMEGBPUSD  SPREADGBPUSD  OPENAUDUSD  HIGHAUDUSD  LOWAUDUSD  CLOSEAUDUSD  VOLUMEAUDUSD  SPREADAUDUSD
date
2021-02-24 16:04:00  1.21274  1.21274  1.21210  1.21219   161.0       5     1.41160     1.41161    1.41106      1.41109          90.0             8     0.79088     0.79088    0.79054      0.79062         115.0             6
2021-02-24 16:05:00  1.21218  1.21228  1.21207  1.21227   166.0       5     1.41108     1.41133    1.41072      1.41095         134.0             8     0.79061     0.79086    0.79042      0.79058         176.0             6
2021-02-24 16:06:00  1.21227  1.21244  1.21221  1.21228   159.0       5     1.41098     1.41123    1.41083      1.41095         139.0             8     0.79056     0.79088    0.79053      0.79061         148.0             6
2021-02-24 16:07:00  1.21228  1.21239  1.21208  1.21215   140.0       5     1.41096     1.41117    1.41078      1.41083         119.0             8     0.79062     0.79078    0.79041      0.79042         137.0             6
2021-02-24 16:08:00  1.21214  1.21237  1.21210  1.21217   149.0       5     1.41083     1.41100    1.41032      1.41032         132.0             8     0.79042     0.79044    0.79021      0.79021         159.0             6
...                      ...      ...      ...      ...     ...     ...         ...         ...        ...          ...           ...           ...         ...         ...        ...          ...           ...           ...
2021-02-24 23:59:00  1.21627  1.21654  1.21626  1.21644    23.0      18     1.41422     1.41435    1.41394      1.41400          63.0            11     0.79632     0.79639    0.79619      0.79623          64.0            16
2021-02-25 00:00:00  1.21652  1.21676  1.21639  1.21666   140.0       5     1.41402     1.41436    1.41397      1.41401          74.0             8     0.79631     0.79649    0.79629      0.79633         113.0             6
2021-02-25 00:01:00  1.21666  1.21669  1.21650  1.21656   287.0       5     1.41404     1.41409    1.41393      1.41408          35.0            13     0.79634     0.79649    0.79631      0.79646          66.0             6
2021-02-25 00:02:00  1.21656  1.21668  1.21652  1.21663   108.0       5     1.41408     1.41408    1.41397      1.41398          24.0            13     0.79646     0.79653    0.79645      0.79649          38.0             7
2021-02-25 00:03:00  1.21663  1.21663  1.21640  1.21650    39.0       5     1.41400     1.41400    1.41398      1.41400           3.0            19     0.79648     0.79648    0.79637      0.79641          17.0            10

```

# history dictionary "array"

#### Short History from Date to Date dict

```python
symbol = "EURUSD"
timeframe = "M1"


history = mt.Shorthistory(symbol,timeframe,10)
print(history)
```

#### History fromDate toDate dict

```python
symbol = "EURUSD"
timeframe = "M1"
fromDate = "24/02/2021"
toDate = "24/02/2021"

history = mt.history(symbol,timeframe,fromDate,toDate)
print(history)


```

# Live data and streaming events

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

```

### Future add comming soon

```

```
