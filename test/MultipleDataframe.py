from ejtraderMT import Metatrader


api = Metatrader()

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"
fromDate = "01/01/2021"
toDate = "01/02/2021"

data = api.historyDataFrame(symbol,symbols,timeframe,fromDate,toDate)



print(data)

