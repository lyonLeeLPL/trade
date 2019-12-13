# coding: UTF-8
import json
import websocket
from time import sleep
from logging import getLogger,INFO,StreamHandler
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)

"""
This program calls Bitflyer real time API JSON-RPC2.0 over Websocket
"""
class RealtimeAPI(object):

    def __init__(self, url, channel):
        self.url = url
        self.channel = channel

        #Define Websocket
        self.ws = websocket.WebSocketApp(self.url,header=None,on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        websocket.enableTrace(True)

    def run(self):
        #ws has loop. To break this press ctrl + c to occur Keyboard Interruption Exception.
        self.ws.run_forever()
        logger.info('Web Socket process ended.')

    """
    Below are callback functions of websocket.
    """
    # when we get message
    def on_message(self, ws, message):
        output = json.loads(message)['params']
        logger.info(output)

    # when error occurs
    def on_error(self, ws, error):
        logger.error(error)

    # when websocket closed.
    def on_close(self, ws):
        logger.info('disconnected streaming server')

    # when websocket opened.
    def on_open(self, ws):
        logger.info('connected streaming server')
        output_json = json.dumps(
            {'method' : 'subscribe',
            'params' : {'channel' : self.channel}
            }
        )
        ws.send(output_json)

if __name__ == '__main__':
    #API endpoint
    url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
    channel = 'lightning_board_snapshot_BTC_JPY'
    json_rpc = RealtimeAPI(url=url, channel=channel)
    #ctrl + cで終了
    json_rpc.run()
