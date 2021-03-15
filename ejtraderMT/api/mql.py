from datetime import datetime, timedelta, date
from pytz import timezone
from tzlocal import get_localzone
from queue import Queue
from threading import Thread
import os
import time

import json
import zmq

import pandas as pd
from ejtraderTH import start
from ejtraderDB import DictSQLite
from tqdm import tqdm

class Functions:
    def __init__(self, host=None, debug=None):
        self.HOST = host or 'localhost'
        self.SYS_PORT = 15555       # REP/REQ port
        self.DATA_PORT = 15556      # PUSH/PULL port
        self.LIVE_PORT = 15557      # PUSH/PULL port
        self.EVENTS_PORT = 15558    # PUSH/PULL port
        self.INDICATOR_DATA_PORT = 15559  # REP/REQ port
        self.CHART_DATA_PORT = 15560  # PUSH 
        self.debug = debug or True

        # ZeroMQ timeout in seconds
        sys_timeout = 100
        data_timeout = 1000

        # initialise ZMQ context
        context = zmq.Context()

        # connect to server sockets
        try:
            self.sys_socket = context.socket(zmq.REQ)
            # set port timeout
            self.sys_socket.RCVTIMEO = sys_timeout * 1000
            self.sys_socket.connect(
                'tcp://{}:{}'.format(self.HOST, self.SYS_PORT))

            self.data_socket = context.socket(zmq.PULL)
            # set port timeout
            self.data_socket.RCVTIMEO = data_timeout * 1000
            self.data_socket.connect(
                'tcp://{}:{}'.format(self.HOST, self.DATA_PORT))

            self.indicator_data_socket = context.socket(zmq.PULL)
            # set port timeout
            self.indicator_data_socket.RCVTIMEO = data_timeout * 1000
            self.indicator_data_socket.connect(
                "tcp://{}:{}".format(self.HOST, self.INDICATOR_DATA_PORT)
            )
            self.chart_data_socket = context.socket(zmq.PUSH)
            # set port timeout
            # TODO check if port is listening and error handling
            self.chart_data_socket.connect(
                "tcp://{}:{}".format(self.HOST, self.CHART_DATA_PORT)
            )

        except zmq.ZMQError:
            raise zmq.ZMQBindError("Binding ports ERROR")
        except KeyboardInterrupt:
            self.sys_socket.close()
            self.sys_socket.term()
            self.data_socket.close()
            self.data_socket.term()
            self.indicator_data_socket.close()
            self.indicator_data_socket.term()
            self.chart_data_socket.close()
            self.chart_data_socket.term()
            pass

    def _send_request(self, data: dict) -> None:
        """Send request to server via ZeroMQ System socket"""
        try:
            self.sys_socket.send_json(data)
            msg = self.sys_socket.recv_string()
            # terminal received the request
            assert msg == 'OK', 'Something wrong on server side'
        except AssertionError as err:
            raise zmq.NotDone(err)
        except zmq.ZMQError:
            raise zmq.NotDone("Sending request ERROR")

        

    def _pull_reply(self):
        """Get reply from server via Data socket with timeout"""
        try:
            msg = self.data_socket.recv_json()
        except zmq.ZMQError:
            raise zmq.NotDone('Data socket timeout ERROR')
        return msg

    def _indicator_pull_reply(self):
        """Get reply from server via Data socket with timeout"""
        try:
            msg = self.indicator_data_socket.recv_json()
        except zmq.ZMQError:
            raise zmq.NotDone("Indicator Data socket timeout ERROR")
        if self.debug:
            print("ZMQ INDICATOR DATA REPLY: ", msg)
        return msg

    def live_socket(self, context=None):
        """Connect to socket in a ZMQ context"""
        try:
            context = context or zmq.Context.instance()
            socket = context.socket(zmq.PULL)
            socket.connect('tcp://{}:{}'.format(self.HOST, self.LIVE_PORT))
        except zmq.ZMQError:
            raise zmq.ZMQBindError("Live port connection ERROR")
        return socket

    def streaming_socket(self, context=None):
        """Connect to socket in a ZMQ context"""
        try:
            context = context or zmq.Context.instance()
            socket = context.socket(zmq.PULL)
            socket.connect('tcp://{}:{}'.format(self.HOST, self.EVENTS_PORT))
        except zmq.ZMQError:
            raise zmq.ZMQBindError("Data port connection ERROR")
        return socket

    def _push_chart_data(self, data: dict) -> None:
        """Send message for chart control to server via ZeroMQ chart data socket"""
        try:
            if self.debug:
                print("ZMQ PUSH CHART DATA: ", data, " -> ", data)
            self.chart_data_socket.send_json(data)
        except zmq.ZMQError:
            raise zmq.NotDone("Sending request ERROR")

    def Command(self, **kwargs) -> dict:
        """Construct a request dictionary from default and send it to server"""

        # default dictionary
        request = {
            "action": None,
            "actionType": None,
            "symbol": None,
            "chartTF": None,
            "fromDate": None,
            "toDate": None,
            "id": None,
            "magic": None,
            "volume": None,
            "price": None,
            "stoploss": None,
            "takeprofit": None,
            "expiration": None,
            "deviation": None,
            "comment": None,
            "chartId": None,
            "indicatorChartId": None,
            "chartIndicatorSubWindow": None,
            "style": None,
        }

        # update dict values if exist
        for key, value in kwargs.items():
            if key in request:
                request[key] = value
            else:
                raise KeyError('Unknown key in **kwargs ERROR')

        # send dict to server
        self._send_request(request)

        # return server reply
        return self._pull_reply()

    def indicator_construct_and_send(self, **kwargs) -> dict:
        """Construct a request dictionary from default and send it to server"""

        # default dictionary
        request = {
            "action": None,
            "actionType": None,
            "id": None,
            "symbol": None,
            "chartTF": None,
            "fromDate": None,
            "toDate": None,
            "name": None,
            "params": None,
            "linecount": None,
        }

        # update dict values if exist
        for key, value in kwargs.items():
            if key in request:
                request[key] = value
            else:
                raise KeyError("Unknown key in **kwargs ERROR")

        # send dict to server
        self._send_request(request)

        # return server reply
        return self._indicator_pull_reply()

    def chart_data_construct_and_send(self, **kwargs) -> dict:
        """Construct a request dictionary from default and send it to server"""

        # default dictionary
        message = {
            "action": None,
            "actionType": None,
            "chartId": None,
            "indicatorChartId": None,
            "data": None,
        }

        # update dict values if exist
        for key, value in kwargs.items():
            if key in message:
                message[key] = value
            else:
                raise KeyError("Unknown key in **kwargs ERROR")

        # send dict to server
        self._push_chart_data(message)


class Metatrader:

    def __init__(self, host=None, real_volume=None, localtime=True):
        self._api = Functions(host)
        self.real_volume = real_volume or False
        self.localtime = localtime 
        self._utc_timezone = timezone('UTC')
        self._my_timezone = get_localzone()
        self._utc_brocker_offset = self.__utc_brocker_offset()
        
       
    
       
        
       
    def balance(self):
        return self._api.Command(action="BALANCE")

    def accountInfo(self):
        return self._api.Command(action="ACCOUNT")

    def positions(self):
        return self._api.Command(action="POSITIONS")

    def orders(self):
        return self._api.Command(action="ORDERS")

    def trade(self, symbol, actionType, volume, stoploss, takeprofit, price, deviation):
        self._api.Command(
            action="TRADE",
            actionType=actionType,
            symbol=symbol,
            volume=volume,
            stoploss=stoploss,
            takeprofit=takeprofit,
            price=price,
            deviation=deviation
        )

    def buy(self, symbol, volume, stoploss, takeprofit, deviation=5):
        price = 0
        self.trade(symbol, "ORDER_TYPE_BUY", volume,
                   stoploss, takeprofit, price, deviation)

    def sell(self, symbol, volume, stoploss, takeprofit, deviation=5):
        price = 0
        self.trade(symbol, "ORDER_TYPE_SELL", volume,
                   stoploss, takeprofit, price, deviation)

    def buyLimit(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_BUY_LIMIT", volume,
                   stoploss, takeprofit, price, deviation)

    def sellLimit(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_SELL_LIMIT", volume,
                   stoploss, takeprofit, price, deviation)

    def buyStop(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_BUY_STOP", volume,
                   stoploss, takeprofit, price, deviation)

    def sellStop(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_SELL_LIMIT", volume,
                   stoploss, takeprofit, price, deviation)

    def cancel_all(self):
        orders = self.orders()

        if 'orders' in orders:
            for order in orders['orders']:
                self.CancelById(order['id'])

    def close_all(self):
        positions = self.positions()

        if 'positions' in positions:
            for position in positions['positions']:
                self.CloseById(position['id'])

    def positionModify(self, id, stoploss, takeprofit):
        self._api.Command(
            action="TRADE",
            actionType="POSITION_MODIFY",
            id=id,
            stoploss=stoploss,
            takeprofit=takeprofit
        )

    def ClosePartial(self, id, volume):
        self._api.Command(
            action="TRADE",
            actionType="POSITION_PARTIAL",
            id=id,
            volume=volume
        )

    def CloseById(self, id):
        self._api.Command(
            action="TRADE",
            actionType="POSITION_CLOSE_ID",
            id=id
        )

    def CloseBySymbol(self, symbol):
        self._api.Command(
            action="TRADE",
            actionType="POSITION_CLOSE_SYMBOL",
            symbol=symbol
        )

    def orderModify(self, id, stoploss, takeprofit, price):
        self._api.Command(
            action="TRADE",
            actionType="ORDER_MODIFY",
            id=id,
            stoploss=stoploss,
            takeprofit=takeprofit,
            price=price
        )

    def CancelById(self, id):
        self._api.Command(
            action="TRADE",
            actionType="ORDER_CANCEL",
            id=id
        )

    def __utc_brocker_offset(self):
        utc = datetime.now(self._utc_timezone).strftime('%Y-%m-%d %H:%M:%S')
        try:
            broker = self.accountInfo()
            broker = datetime.strptime(broker['time'], '%Y.%m.%d %H:%M:%S')
        except KeyError:
            raise "Metatrader 5 Server is disconnect"
        utc = datetime.strptime(utc, '%Y-%m-%d %H:%M:%S')

        duration = broker - utc
        duration_in_s = duration.total_seconds()
        hour = divmod(duration_in_s, 60)[0]
        seconds = int(hour)*60
        return seconds

    
    def _price(self):
        connect = self._api.live_socket()
        while True:
            price = connect.recv_json()
            try:
                price = price['data']
                price = pd.DataFrame([price]) 
                price = price.set_index([0])
                price.index.name = 'date'
                if self._allchartTF == 'TICK':
                    price.index = pd.to_datetime(price.index, unit='ms')
                    price.columns = ['bid', 'ask']
                    self._priceQ.put(price)
                else:
                    if self.real_volume:
                        del price[5]
                    else:
                        del price[6]
                    price.index = pd.to_datetime(price.index, unit='s')
                    price.columns = ['open', 'high', 'low','close', 'volume','spread']
                    self._priceQ.put(price)
                    
                
            except KeyError:
                  pass

       

    def _start_thread_price(self):
        t = Thread(target=self._price,daemon=True)
        t.start()
        self._priceQ = Queue()

    def _start_thread_event(self):
        t = Thread(target=self._event,daemon=True)
        t.start()
        self._eventQ = Queue()
        

    

    def _event(self):
        connect = self._api.streaming_socket()
        while True:
            event = connect.recv_json()
            try:
                event = event['request']
                event = pd.DataFrame(event, index=[0])
                self._eventQ.put(event)
            except KeyError:
                pass

    def price(self, symbol, chartTF):
        self._api.Command(action="RESET")
        self._allsymbol_ = symbol
        self._allchartTF = chartTF
        for active in symbol:
            self._api.Command(action="CONFIG", symbol=active, chartTF=chartTF) 
        self._start_thread_price()        
        time.sleep(0.5)
        return  self._priceQ.get()
       


    def event(self, symbol, chartTF):
        self._api.Command(action="RESET")
        self._allsymbol_ = symbol
        self._allchartTF = chartTF
        for active in symbol:
            self._api.Command(action="CONFIG",  symbol=active, chartTF=chartTF)          
        
        self._start_thread_event()
        time.sleep(0.5)
        return  self._eventQ.get()
        

    
      

    # convert datestamp to dia/mes/ano
    def _date_to_timestamp(self, s):
        return time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
    # convert datestamp to dia/mes/ano
    def datetime_to_timestamp(self, s):
        return time.mktime(s.timetuple())

    def _date_to_timestamp_broker(self):
        brokertime = time.mktime(datetime.strptime(self.accountInfo()['time'], '%Y.%m.%d %H:%M:%S').timetuple())
        return round(brokertime)

    def _brokerTimeCalculation(self,s):
        delta = timedelta(seconds = s)
        broker = datetime.strptime(self.accountInfo()['time'], '%Y.%m.%d %H:%M:%S')
        result = broker - delta
        return result
  

    


    def _timeframe_to_sec(self, timeframe):
        # Timeframe dictionary
        TIMECANDLE = {
            "M1": 60,
            "M2": 120,
            "M3": 180,
            "M4": 240,
            "M5": 300,
            "M15": 900,
            "M30": 1800,
            "H1": 3600,
            "H4": 14400,
            "D1": 86400,
            "W1": 604800,
            "MN": 2629746,

        }
        return TIMECANDLE[timeframe]

    def _setlocaltime_dataframe(self, df):
        df.index = df.index.tz_localize(self._utc_brocker_offset)
        df.index = df.index.tz_convert(self._my_timezone)
        df.index = df.index.tz_localize(None)
        return df
   


    def history(self,symbol,chartTF=None,fromDate=None,toDate=None,database=None):
        self.chartTF = chartTF
        self.fromDate = fromDate
        self.toDate = toDate
        self._historyQ = Queue()
        if isinstance(symbol, tuple):
            for symbols in symbol:
                self._symbol = symbols
        else:
            self._symbol = symbol
        if chartTF:
            if database:
                try:
                    start(self.__historyThread_save,repeat=1, max_threads=20)
                except:
                    print("Error: unable to start History thread")
            else:
                try:
                    start(self._historyThread,repeat=1, max_threads=20)
                except:
                    print("Error: unable to start History thread")
                return self._historyQ.get()
        else:
            q = DictSQLite('history')
            if isinstance(symbol, list):
                try:
                    df = q[f'{self._symbol[0]}']
                except KeyError:
                    df = f" {self._symbol[0]}  isn't on database"
                    pass 
            else:
                try:
                    df = q[f'{self._symbol}']
                except KeyError:
                    df = f" {self._symbol}  isn't on database"
                    pass
            return df
    
       


    def _historyThread(self,data):
        actives = self._symbol
        chartTF = self.chartTF
        fromDate = self.fromDate
        toDate  = self.toDate
        main = pd.DataFrame()
        current = pd.DataFrame()
        if(chartTF == 'TICK'):
            chartConvert = 60
        else:
            chartConvert = self._timeframe_to_sec(chartTF)
        for active in actives:
            # the first symbol on list is the main and the rest will merge
            if active == actives[0]:
                # get data
                if fromDate and toDate:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self._date_to_timestamp(fromDate), toDate=self._date_to_timestamp(toDate))
                elif isinstance(fromDate, int):
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + fromDate * chartConvert - chartConvert) ))
                elif isinstance(fromDate, str) and toDate==None:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self._date_to_timestamp(fromDate),toDate=self._date_to_timestamp_broker())
                else:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + 100 * chartConvert - chartConvert) ))
                self._api.Command(action="RESET")
                try:
                    main = pd.DataFrame(data['data'])
                    main = main.set_index([0])
                    main.index.name = 'date'
                    

                    # TICK DATA
                    if(chartTF == 'TICK'):
                        main.columns = ['bid', 'ask']
                        main.index = pd.to_datetime(main.index, unit='ms')
                    else:
                        main.index = pd.to_datetime(main.index, unit='s')
                        if self.real_volume:
                            del main[5]
                        else:
                            del main[6]
                        main.columns = ['open', 'high', 'low',
                                        'close', 'volume', 'spread']
                except KeyError:
                    pass
            else:
                 # get data
                if fromDate and toDate:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self._date_to_timestamp(fromDate), toDate=self._date_to_timestamp(toDate))
                elif isinstance(fromDate, int):
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + fromDate * chartConvert - chartConvert) ))
                elif isinstance(fromDate, str) and toDate==None:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self._date_to_timestamp(fromDate),toDate=self._date_to_timestamp_broker())
                else:
                    data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + 100 * chartConvert - chartConvert) ))

                self._api.Command(action="RESET")
                try:
                    current = pd.DataFrame(data['data'])
                    current = current.set_index([0])
                    current.index.name = 'date'
                    active = active.lower()
                    # TICK DATA
                    if(chartTF == 'TICK'):
                        current.index = pd.to_datetime(current.index, unit='ms')
                        current.columns = [f'{active}_bid', f'{active}_ask']
                    else:
                        current.index = pd.to_datetime(current.index, unit='s')
                        if self.real_volume:
                            del current[5]
                        else:
                            del current[6]
            
                        current.columns = [f'{active}_open', f'{active}_high',
                                        f'{active}_low', f'{active}_close', f'{active}_volume', f'{active}_spread']

                    main = pd.merge(main, current, how='inner',
                                    left_index=True, right_index=True)
                except KeyError:
                    pass
        try:
            if self.localtime:
                self._setlocaltime_dataframe(main)
        except AttributeError:
            pass
        main = main.loc[~main.index.duplicated(keep='first')]
        self._historyQ.put(main)

    

    def __historyThread_save(self,data):
            actives = self._symbol
            chartTF = self.chartTF
            fromDate = self.fromDate
            toDate  = self.toDate
            main = pd.DataFrame()
            current = pd.DataFrame()
            self._count = 0
            try:
                os.makedirs('DataBase')
            except OSError:
                pass
            # count data
            start_date = datetime.strptime(fromDate, "%d/%m/%Y")
            if not toDate:
                end_date = datetime.now() #date(2021, 1, 1)
            else:
                end_date = datetime.strptime(toDate, "%d/%m/%Y")

            delta = timedelta(days=1)
            delta2 = timedelta(days=1)
            diff_days = start_date - end_date
            days_count = diff_days.days
            pbar = tqdm(total=abs(days_count))
            appended_data = []
            while start_date <= end_date:
                pbar.update(delta.days)
                fromDate = start_date.strftime("%d/%m/%Y")
                toDate = start_date
                toDate +=  delta2
                toDate = toDate.strftime("%d/%m/%Y")  

                if(chartTF == 'TICK'):
                    chartConvert = 60
                else:
                    chartConvert = self._timeframe_to_sec(chartTF)
                for active in actives:
                    self._count += 1 
                   
                    # the first symbol on list is the main and the rest will merge
                    if active == actives[0]:
                        self._active_file = active
                        # get data
                        if fromDate and toDate:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self._date_to_timestamp(fromDate), toDate=self._date_to_timestamp(toDate))
                        elif isinstance(fromDate, int):
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + fromDate * chartConvert - chartConvert) ))
                        elif isinstance(fromDate, str) and toDate==None:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self._date_to_timestamp(fromDate),toDate=self._date_to_timestamp_broker())
                        else:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + 100 * chartConvert - chartConvert) ))
                        self._api.Command(action="RESET")
                        try:
                            main = pd.DataFrame(data['data'])
                            main = main.set_index([0])
                            main.index.name = 'date'
                            

                            # TICK DATA
                            if(chartTF == 'TICK'):
                                main.columns = ['bid', 'ask']
                                main.index = pd.to_datetime(main.index, unit='ms')
                            else:
                                main.index = pd.to_datetime(main.index, unit='s')
                                if self.real_volume:
                                    del main[5]
                                else:
                                    del main[6]
                                main.columns = ['open', 'high', 'low',
                                                'close', 'volume', 'spread']
                        except KeyError:
                            pass
                    else:
                        # get data
                        if fromDate and toDate:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self._date_to_timestamp(fromDate), toDate=self._date_to_timestamp(toDate))
                        elif isinstance(fromDate, int):
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + fromDate * chartConvert - chartConvert) ))
                        elif isinstance(fromDate, str) and toDate==None:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self._date_to_timestamp(fromDate),toDate=self._date_to_timestamp_broker())
                        else:
                            data = self._api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                                fromDate=self.datetime_to_timestamp(self._brokerTimeCalculation((10800 + chartConvert) + 100 * chartConvert - chartConvert) ))

                        self._api.Command(action="RESET")
                        try:
                            current = pd.DataFrame(data['data'])
                            current = current.set_index([0])
                            current.index.name = 'date'
                            active = active.lower()
                            # TICK DATA
                            if(chartTF == 'TICK'):
                                current.index = pd.to_datetime(current.index, unit='ms')
                                current.columns = [f'{active}_bid', f'{active}_ask']
                            else:
                                current.index = pd.to_datetime(current.index, unit='s')
                                if self.real_volume:
                                    del current[5]
                                else:
                                    del current[6]
                    
                                current.columns = [f'{active}_open', f'{active}_high',
                                                f'{active}_low', f'{active}_close', f'{active}_volume', f'{active}_spread']

                            main = pd.merge(main, current, how='inner',
                                            left_index=True, right_index=True)
                        except KeyError:
                            pass
                try:
                    if self.localtime:
                        self._setlocaltime_dataframe(main)
                except AttributeError:
                    pass
                main = main.loc[~main.index.duplicated(keep='first')]
                appended_data.append(main)
             
                start_date += delta
            pbar.close()
            df = pd.concat(appended_data)
            start(self._save_to_db,data=[df],repeat=1, max_threads=20)



    def _save_to_db(self,df):
        q = DictSQLite('history',multithreading=True)
        q[f"{self._active_file}"] = df
        
            




    

    
   