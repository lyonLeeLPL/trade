# coding: UTF-8
import json
import websocket
from datetime import datetime, timedelta
import dateutil.parser
import concurrent.futures
import collections
import numpy as np
from time import sleep
from logging import getLogger,INFO,StreamHandler
import pandas as pd
import csv
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)

TICK_RES = 1 # OHLCV データの解像度(1分足 : 60, 5分足 : 300, 10分足 : 600, ...)
OHLCV_LEN = 5 # OHLCV データの保持数、指定数+1 を管理(0番目は最新データ(随時更新)、1番目以降が確定データ)
IDX_DATE = 0
IDX_OPEN = 1
IDX_HIGH = 2
IDX_LOW = 3
IDX_CLOSE = 4
IDX_VOLUME = 5
ITV_SLEEP_WSS_RECONNECT = 1

DATA_DIR = 'data/ohlcv/'
SINCE = datetime(2018, 8, 3)
RES_NUM = 1 # 解像度
RES_UNIT = "s" # 解像度
RES_SEC = RES_NUM * (1 if RES_UNIT == "s" else 60 if RES_UNIT == "m" else 60*60)

# Pandas Dataframe
# inCsvPath = DATA_DIR + SINCE.strftime("%Y%m%d") + ".csv"
# df = pd.read_csv(inCsvPath, header=None, names=["T", "O", "H", "L", "C", "V"], parse_dates=["T"])

"""
This program calls Bitflyer real time API JSON-RPC2.0 over Websocket
"""
class RealtimeOHLCV(object):
  def __init__(self, url, channel):
    self.url = url
    self.channel = channel

    #Define Websocket
    self.ws = websocket.WebSocketApp(self.url, header=None, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
    websocket.enableTrace(True)

  def init_ohlcvs(self):
    self.ohlcvs = collections.deque([], OHLCV_LEN + 1)
    self.firstTick = self.get_tick_datetime(datetime.now() + timedelta(seconds=TICK_RES))
    for i in range(0, OHLCV_LEN + 1):
      self.ohlcvs.appendleft([0, 0.0, 0.0, 0.0, 0.0, 0.0])

  def run(self):
    #ws has loop. To break this press ctrl + c to occur Keyboard Interruption Exception.
    while(True):
      self.init_ohlcvs()
      self.ws.run_forever()
      logger.info('Web Socket process ended. Retrying reconnect.')
      self.ohlcvs.clear()
      sleep(ITV_SLEEP_WSS_RECONNECT)

  def is_alive(self):
    return self.ws.keep_running

  """
  Below are callback functions of websocket.
  """
  # when we get message
  def on_message(self, ws, message):
    output = json.loads(message)['params']
    self.create_ohlcv(output)

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

  """
  Below are OHLCV functions.
  """
  # OHLCV 生成
  def create_ohlcv(self, output):
    now = datetime.now()
    for d in output["message"]:
      exec_date = self.get_exec_datetime(d)

      # 中途半端な時刻のデータは捨てる
      if(self.firstTick > exec_date):
        break

      # 約定データが確定足の分は捨てる
      if(self.is_past_data(exec_date, now)):
        continue

      # OHLCV データの時刻が更新された場合
      if(self.is_next_tick(exec_date)):
        if(self.ohlcvs[0][IDX_DATE] != 0):
          # ローテーション(古いデータを上書きして再利用)
          self.ohlcvs.rotate()
        # OHLCV データ初期値設定
        self.init_ohlcv(exec_date, d)

      # OHLCV データの時刻が同じ場合
      else:
        # OHLCV データ更新
        self.update_ohlcv(d)

  # 約定データから datetime 生成
  def get_exec_datetime(self, d):
    exec_date = d["exec_date"].replace('T', ' ')[:-1]
    return dateutil.parser.parse(exec_date) + timedelta(hours=9)

  # OHLCV データの基準時刻
  def get_tick_datetime(self, dt):
    tickTs = int(dt.timestamp() / TICK_RES) * TICK_RES
    return datetime.fromtimestamp(tickTs)

  # 足が確定した後に受信したデータか
  def is_past_data(self, exec_date, now):
    return self.get_tick_datetime(exec_date) < self.get_tick_datetime(now)

  # 次の足かどうか
  def is_next_tick(self, exec_date):
    return self.get_tick_datetime(datetime.fromtimestamp(self.ohlcvs[0][IDX_DATE])) != self.get_tick_datetime(exec_date)

  def init_ohlcv(self, exec_date, d):
    price = float(d["price"])
    vol = float(d["size"])
    self.ohlcvs[0][IDX_DATE] = self.get_tick_datetime(exec_date).timestamp()
    self.ohlcvs[0][IDX_OPEN] = price
    self.ohlcvs[0][IDX_HIGH] = price
    self.ohlcvs[0][IDX_LOW] = price
    self.ohlcvs[0][IDX_CLOSE] = price
    self.ohlcvs[0][IDX_VOLUME] = vol

  def update_ohlcv(self, d):
    price = float(d["price"])
    vol = float(d["size"])
    self.ohlcvs[0][IDX_HIGH] = max(self.ohlcvs[0][IDX_HIGH], price)
    self.ohlcvs[0][IDX_LOW] = min(self.ohlcvs[0][IDX_LOW], price)
    self.ohlcvs[0][IDX_CLOSE] = price
    self.ohlcvs[0][IDX_VOLUME] += vol

  # 最新(更新中)の OHLCV 取得
  def get_current_ohlcv(self):
    return self.ohlcvs[0]

  # 確定済の最新 OHLCV 取得
  def get_newest_ohlcv(self):
    return self.ohlcvs[1]

  # OHLCV 取得
  # デフォルト: 新しい順で全てのデータを取得
  def get_ohlcvs(self, num=OHLCV_LEN+1, asc=False):
    ohlcvs = []
    for i in range(0, num):
      ohlcvs.append(self.ohlcvs[i])
    if(asc):
      ohlcvs.reverse()
    return ohlcvs

def print_ohlcv(rtOHLCV):
  prevData = rtOHLCV.get_current_ohlcv()
  # #出力ファイル
  # outCsvPath = DATA_DIR + SINCE.strftime("%Y%m%d") + "_" + str(RES_NUM) + RES_UNIT + ".csv"
  # outCsv = open(outCsvPath, mode="a")
  # writer = csv.writer(outCsv)
  while(True):
      #出力ファイル
    outCsvPath = "data/ohlcv/test.csv"
    outCsv = open(outCsvPath, mode="a")
    writer = csv.writer(outCsv)
    # OHLCV データが更新されたら出力
    if(rtOHLCV.is_alive()):
      tempData = rtOHLCV.get_current_ohlcv()
      if(tempData != prevData):
        ohlcv = rtOHLCV.get_newest_ohlcv()
        a = [datetime.fromtimestamp(ohlcv[IDX_DATE]), ohlcv[IDX_OPEN], ohlcv[IDX_HIGH], ohlcv[IDX_LOW], ohlcv[IDX_CLOSE], ohlcv[IDX_VOLUME]]
        logger.info("{},{},{},{},{},{}".format(a[0], a[1], a[2], a[3], a[4], a[5]))
        writer.writerow(a)
        prevData = tempData
        sleep(TICK_RES * 0.9)
        continue
    sleep(0.5)

if __name__ == '__main__':
  # Thread
  executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
  #API endpoint
  url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
  channel = 'lightning_executions_FX_BTC_JPY' # 約定
  rtOHLCV = RealtimeOHLCV(url=url, channel=channel)
  #ctrl + cで終了
  executor.submit(rtOHLCV.run)
  executor.submit(print_ohlcv, rtOHLCV)
