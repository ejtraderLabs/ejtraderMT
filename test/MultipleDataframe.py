from ejtraderMT import Metatrader


api = Metatrader()

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"
fromDate = "24/02/2021"
toDate = "26/02/2021"

data = api.historyDataFrame(symbol,timeframe,fromDate,toDate,True)



print(data)

