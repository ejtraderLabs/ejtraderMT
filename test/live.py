from ejtraderMT import Metatrader
from ejtraderDB import DictSQLite
import time

api = Metatrader()
symbols = ["EURUSD"]
timeframe = "M1"


# dados = api.history(symbols,timeframe,5)

# start_time = time.perf_counter()
# dados = api.history(symbols,timeframe,150,threadON=True)
# df = dados[symbols[0]]
# end_time = time.perf_counter()
# elapsed_time = end_time - start_time
# print(f"Elapsed run time: {elapsed_time} seconds")

# print(df)

# start_time = time.perf_counter()
# dados = api.history(symbols,timeframe,1)
# end_time = time.perf_counter()
# elapsed_time = end_time - start_time
# print(f"Elapsed run time: {elapsed_time} seconds")

# print(dados)


# price = api.price(symbols,timeframe)


while True:
    history = api.history(symbols,timeframe,5)
    print(history)
    # print(price)
