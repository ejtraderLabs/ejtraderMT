import json
import zmq
import pandas as pd
from datetime import datetime, timedelta
import time
from pytz import timezone
from tzlocal import get_localzone


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

    def __init__(self, host=None, real_volume=None, localtime=None):
        self.api = Functions(host)
        self.real_volume = real_volume or False
        self.localtime = localtime or False
        self.utc_timezone = timezone('UTC')

        self.live_price = self.api.live_socket()
        self.live_event = self.api.streaming_socket()
        self.my_timezone = get_localzone()
        self.utc_brocker_offset = self._utc_brocker_offset()
       
    def balance(self):
        return self.api.Command(action="BALANCE")

    def accountInfo(self):
        return self.api.Command(action="ACCOUNT")

    def positions(self):
        return self.api.Command(action="POSITIONS")

    def orders(self):
        return self.api.Command(action="ORDERS")

    def trade(self, symbol, actionType, volume, stoploss, takeprofit, price, deviation):
        self.api.Command(
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
        self.api.Command(
            action="TRADE",
            actionType="POSITION_MODIFY",
            id=id,
            stoploss=stoploss,
            takeprofit=takeprofit
        )

    def ClosePartial(self, id, volume):
        self.api.Command(
            action="TRADE",
            actionType="POSITION_PARTIAL",
            id=id,
            volume=volume
        )

    def CloseById(self, id):
        self.api.Command(
            action="TRADE",
            actionType="POSITION_CLOSE_ID",
            id=id
        )

    def CloseBySymbol(self, symbol):
        self.api.Command(
            action="TRADE",
            actionType="POSITION_CLOSE_SYMBOL",
            symbol=symbol
        )

    def orderModify(self, id, stoploss, takeprofit, price):
        self.api.Command(
            action="TRADE",
            actionType="ORDER_MODIFY",
            id=id,
            stoploss=stoploss,
            takeprofit=takeprofit,
            price=price
        )

    def CancelById(self, id):
        self.api.Command(
            action="TRADE",
            actionType="ORDER_CANCEL",
            id=id
        )

    def _utc_brocker_offset(self):
        utc = datetime.now(self.utc_timezone).strftime('%Y-%m-%d %H:%M:%S')
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

   
    


    # convert datestamp to dia/mes/ano
    def date_to_timestamp(self, s):
        return time.mktime(datetime.strptime(s, "%d/%m/%Y").timetuple())
    # convert datestamp to dia/mes/ano
    def datetime_to_timestamp(self, s):
        return time.mktime(s.timetuple())

    def date_to_timestamp_broker(self):
        brokertime = time.mktime(datetime.strptime(self.accountInfo()['time'], '%Y.%m.%d %H:%M:%S').timetuple())
        return round(brokertime)

    def brokerTimeCalculation(self,s):
        delta = timedelta(seconds = s)
        broker = datetime.strptime(self.accountInfo()['time'], '%Y.%m.%d %H:%M:%S')
        result = broker - delta
        print(result)
        return result

    

    # convert timestamp to hour minitus secods
    def convertTimeStamp(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def live(self, symbol, chartTF):
        self.api.Command(action="RESET")
        for active in symbol:
            self.api.Command(action="CONFIG",  symbol=active, chartTF=chartTF)
            print(f'subscribed : {active}')
            time.sleep(1)


    def timeframe_to_sec(self, timeframe):
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

    def setlocaltime_dataframe(self, df):
        df.index = df.index.tz_localize(self.utc_brocker_offset)
        df.index = df.index.tz_convert(self.my_timezone)
        df.index = df.index.tz_localize(None)
        return df

    def history(self, symbol, chartTF, fromDate=None, toDate=None):
        actives = symbol
        main = pd.DataFrame()
        current = pd.DataFrame()
        for active in actives:
            # the first symbol on list is the main and the rest will merge
            if active == symbol[0]:
                # get data
                if fromDate and toDate:
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.date_to_timestamp(fromDate), toDate=self.date_to_timestamp(toDate))
                elif isinstance(fromDate, int):
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self.brokerTimeCalculation((10800 + self.timeframe_to_sec(chartTF)) + fromDate * self.timeframe_to_sec(chartTF) - self.timeframe_to_sec(chartTF)) ))
                elif isinstance(fromDate, str) and toDate==None:
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.date_to_timestamp(fromDate),toDate=self.date_to_timestamp_broker())
                else:
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self.brokerTimeCalculation((10800 + self.timeframe_to_sec(chartTF)) + 100 * self.timeframe_to_sec(chartTF) - self.timeframe_to_sec(chartTF)) ))
                self.api.Command(action="RESET")
                try:
                    main = pd.DataFrame(data['data'])
                    main = main.set_index([0])
                    main.index.name = 'date'
                    main.index = pd.to_datetime(main.index, unit='s')

                    # TICK DATA
                    if(chartTF == 'TICK'):
                        main.columns = ['bid', 'ask']
                    else:
                        # OHLC DATA
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
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.date_to_timestamp(fromDate), toDate=self.date_to_timestamp(toDate))
                elif isinstance(fromDate, int):
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self.brokerTimeCalculation((10800 + self.timeframe_to_sec(chartTF)) + fromDate * self.timeframe_to_sec(chartTF) - self.timeframe_to_sec(chartTF)) ))
                elif isinstance(fromDate, str) and toDate==None:
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.date_to_timestamp(fromDate),toDate=self.date_to_timestamp_broker())
                else:
                    data = self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF,
                                        fromDate=self.datetime_to_timestamp(self.brokerTimeCalculation((10800 + self.timeframe_to_sec(chartTF)) + 100 * self.timeframe_to_sec(chartTF) - self.timeframe_to_sec(chartTF)) ))

                self.api.Command(action="RESET")
                try:
                    current = pd.DataFrame(data['data'])
                    current = current.set_index([0])
                    current.index.name = 'date'
                    current.index = pd.to_datetime(current.index, unit='s')
                    active = active.lower()
                    # TICK DATA
                    if(chartTF == 'TICK'):
                        current.columns = [f'{active}_bid', f'{active}_ask']
                    else:
                        # OHLC DATA
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
                self.setlocaltime_dataframe(main)
        except AttributeError:
            pass
        main = main.loc[~main.index.duplicated(keep='first')]
        return main

   