import persistqueue
from ejtraderMT import Metatrader
from datetime import date, timedelta
import time
import pandas as pd
import os

start_time = time.time()
api = Metatrader()


active = ['EURUSD','GBPUSD','EURJPY']
timeframe = "M1"

# q = persistqueue.SQLiteQueue(f'data/{symbol}', auto_commit=True)
try:
    os.makedirs('data')
except OSError:
    pass


start_date = date(2020, 1, 1)
end_date = date(2020, 2, 1)
delta = timedelta(days=1)
delta2 = timedelta(days=1)

while start_date <= end_date:
    fromDate = start_date.strftime('%d/%m/%Y')
    toDate = start_date
    toDate +=  delta2
    toDate = toDate.strftime('%d/%m/%Y')
    for symbol in active:
        data = api.historyDataFrame(symbol,timeframe, fromDate,toDate)
        print(data)
        data.to_csv (f'data/{symbol}.csv', index = True, header=True)
        print(f'writing to Database... from: {fromDate} to {toDate} symbol: {symbol}')
        start_date += delta
         

for symbol in active:
    q = persistqueue.SQLiteQueue(f'data/{symbol}', auto_commit=True)
    df = pd.read_csv(f'data/{symbol}.csv')
    q.put(df)
    # Get directory name
    MODELFILE = f'data/{symbol}.csv'
    try:
        os.remove(MODELFILE)
    except OSError:
        pass

print(("--- %s seconds ---" % (time.time() - start_time)))    



        











