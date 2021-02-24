from ejtraderMT import Metatrader



api = Metatrader()

data = api.history("EURUSD","M1","20/02/2021","24/02/2021")


print(data)

