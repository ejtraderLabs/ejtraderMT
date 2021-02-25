from ejtraderMT import Metatrader


api = Metatrader()

symbol = "EURUSD"
timeframe = "M1"
fromDate = "01/01/2021"
toDate = "01/02/2021"

data = api.history(symbol,timeframe,fromDate,toDate)


print(data)

