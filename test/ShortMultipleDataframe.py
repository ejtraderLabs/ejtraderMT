from ejtraderMT import Metatrader



api = Metatrader('192.168.1.101')

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"


data = api.ShorthistoryMultiDataFrame(symbol,symbols,timeframe,3,True)


print(data)

