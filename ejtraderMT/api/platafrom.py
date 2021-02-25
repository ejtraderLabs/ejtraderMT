import json
import zmq
from .helpers.utils import convertDate
import pandas as pd
from datetime import datetime
import time

class Functions:
    def __init__(self, host=None):
        self.HOST = host or 'localhost'
        self.SYS_PORT = 15555       # REP/REQ port
        self.DATA_PORT = 15556      # PUSH/PULL port
        self.LIVE_PORT = 15557      # PUSH/PULL port
        self.EVENTS_PORT = 15558    # PUSH/PULL port
        self.INDICATOR_DATA_PORT = 15559  # REP/REQ port
        self.CHART_DATA_PORT = 15560  # PUSH port

        # ZeroMQ timeout in seconds
        sys_timeout = 10
        data_timeout = 100

        # initialise ZMQ context
        context = zmq.Context()

        # connect to server sockets
        try:
            self.sys_socket = context.socket(zmq.REQ)
            # set port timeout
            self.sys_socket.RCVTIMEO = sys_timeout * 1000
            self.sys_socket.connect('tcp://{}:{}'.format(self.HOST, self.SYS_PORT))

            self.data_socket = context.socket(zmq.PULL)
            # set port timeout
            self.data_socket.RCVTIMEO = data_timeout * 1000
            self.data_socket.connect('tcp://{}:{}'.format(self.HOST, self.DATA_PORT))

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

    def __init__(self,host=None):
        self.api = Functions(host)
        self.livePrice = self.api.live_socket()
        self. liveEvent = self.api.streaming_socket()
                 
        

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
        price=0
        self.trade(symbol, "ORDER_TYPE_BUY", volume, stoploss, takeprofit, price, deviation)

    def sell(self, symbol, volume, stoploss, takeprofit, deviation=5):
        price=0
        self.trade(symbol, "ORDER_TYPE_SELL", volume, stoploss, takeprofit, price, deviation)

    def buyLimit(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_BUY_LIMIT", volume, stoploss, takeprofit, price, deviation)

    def sellLimit(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_SELL_LIMIT", volume, stoploss, takeprofit, price, deviation)

    def buyStop(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_BUY_STOP", volume, stoploss, takeprofit, price, deviation)

    def sellStop(self, symbol, volume, stoploss, takeprofit, price=0, deviation=5):
        self.trade(symbol, "ORDER_TYPE_SELL_LIMIT", volume, stoploss, takeprofit, price, deviation)

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

    def accountInfo(self):
        return json.loads(json.dumps(self.api.Command(action="ACCOUNT")))

    def positions(self):
        return json.loads(json.dumps(self.api.Command(action="POSITIONS")))

    def orders(self):
        return json.loads(json.dumps(self.api.Command(action="ORDERS")))


    def Shorthistory(self, symbol, chartTF, fromDate, toDate):
       
        if(chartTF == 'TICK'):
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * 60))))
            self.api.Command(action="RESET")
        else:
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * (self.timeframe_to_sec(chartTF) * 60)))))
            self.api.Command(action="RESET")
        return data


    def history(self, symbol, chartTF, fromDate, toDate):
       
        if(chartTF == 'TICK'):
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
            self.api.Command(action="RESET")
        else:
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
            self.api.Command(action="RESET")
        return data


    def historyDataframe(self, symbol, chartTF, fromDate, toDate):
       
        if(chartTF == 'TICK'):
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
            data_frame = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
            data_frame = data_frame.set_index(['date'])
            data_frame.index = pd.to_datetime(data_frame.index,unit='s')
            self.api.Command(action="RESET")
        else:
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
            data_frame = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
            data_frame = data_frame.set_index(['date'])
            data_frame.index = pd.to_datetime(data_frame.index,unit='s')
            self.api.Command(action="RESET")
        return data_frame
    def timeframe_to_sec(self, timeframe):
            # Timeframe dictionary
            TIMECANDLE = {
                "S30": 30,
                "M1": 60,
                "M2": 120,
                "M3": 180,
                "M4": 240,
                "M5": 300,
                "M15": 900,
                "M30": 1800,
                "H1": 3600,
                    
            }
            return TIMECANDLE[timeframe]  


    def ShorthistoryDataframe(self, symbol, chartTF, fromDate):
        
        if(chartTF == 'TICK'):
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * 60))))
            data_frame = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
            data_frame = data_frame.set_index(['date'])
            data_frame.index = pd.to_datetime(data_frame.index,unit='s')
            self.api.Command(action="RESET")
        else:
            data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=symbol, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * (self.timeframe_to_sec(chartTF) * 60)))))
            data_frame = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
            data_frame = data_frame.set_index(['date'])
            data_frame.index = pd.to_datetime(data_frame.index,unit='s')
            self.api.Command(action="RESET")
        return data_frame
   


    def historyMultiDataFrame(self, symbol, symbols, chartTF, fromDate, toDate):
        actives = symbols
        main = pd.DataFrame()
        current = pd.DataFrame()

        for active in actives:
            if active == symbol:
                if(chartTF == 'TICK'):
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
                    main = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
                    main = main.set_index(['date'])
                    main.index = pd.to_datetime(main.index,unit='s')
                    self.api.Command(action="RESET")
                else:
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
                    main = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
                    main = main.set_index(['date'])
                    main.index = pd.to_datetime(main.index,unit='s')
                    self.api.Command(action="RESET")
                
            else:
                if(chartTF == 'TICK'):
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
                    current = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
                    current = current.set_index(['date'])
                    current.index = pd.to_datetime(current.index,unit='s')
                    current.columns = [f'BID{active}',f'ASK{active}']
                    self.api.Command(action="RESET")
                    main = pd.merge(main,current, how='inner', left_index=True, right_index=True)
                else:
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=convertDate(fromDate), toDate=convertDate(toDate))))
                    current = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
                    current = current.set_index(['date'])
                    current.index = pd.to_datetime(current.index,unit='s')
                    current.columns = [f'OPEN{active}',f'HIGH{active}',f'LOW{active}',f'CLOSE{active}',f'VOLUME{active}',f'SPREAD{active}']
                    self.api.Command(action="RESET")
                    main = pd.merge(main,current, how='inner', left_index=True, right_index=True)
        main = main.loc[~main.index.duplicated(keep = 'first')]
        return main

    def ShorthistoryMultiDataFrame(self, symbol, symbols, chartTF, fromDate):
        actives = symbols
        main = pd.DataFrame()
        current = pd.DataFrame()

        for active in actives:
            if active == symbol:
                if(chartTF == 'TICK'):
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * 60))))
                    main = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
                    main = main.set_index(['date'])
                    main.index = pd.to_datetime(main.index,unit='s')
                    self.api.Command(action="RESET")
                else:
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * (self.timeframe_to_sec(chartTF) * 60)))))
                    main = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
                    main = main.set_index(['date'])
                    main.index = pd.to_datetime(main.index,unit='s')
                    self.api.Command(action="RESET")
                
            else:
                if(chartTF == 'TICK'):
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * 60))))
                    current = pd.DataFrame(data['data'], columns=['date', 'bid', 'ask'])
                    current = current.set_index(['date'])
                    current.index = pd.to_datetime(current.index,unit='s')
                    current.columns = [f'BID{active}',f'ASK{active}']
                    self.api.Command(action="RESET")
                    main = pd.merge(main,current, how='inner', left_index=True, right_index=True)
                else:
                    data = json.loads(json.dumps(self.api.Command(action="HISTORY", actionType="DATA", symbol=active, chartTF=chartTF, fromDate=datetime.utcnow().timestamp() - (fromDate * (self.timeframe_to_sec(chartTF) * 60)))))
                    current = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low','close','volume','spread'])
                    current = current.set_index(['date'])
                    current.index = pd.to_datetime(current.index,unit='s')
                    current.columns = [f'OPEN{active}',f'HIGH{active}',f'LOW{active}',f'CLOSE{active}',f'VOLUME{active}',f'SPREAD{active}']
                    self.api.Command(action="RESET")
                    main = pd.merge(main,current, how='inner', left_index=True, right_index=True)
        main = main.loc[~main.index.duplicated(keep = 'first')]
        return main


    
    

  

 
         



  

   
