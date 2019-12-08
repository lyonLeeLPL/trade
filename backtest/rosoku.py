# coding:utf-8
import ccxt
from datetime import datetime, timedelta
import dateutil.parser
from time import sleep
from logging import getLogger,INFO,FileHandler
logger = getLogger(__name__)

SYMBOL_BTCFX = 'FX_BTC_JPY'
ITV_SLEEP = 0.001

def get_exec_datetime(d):
  exec_date = d["exec_date"].replace('T', ' ')[:-1]
  return dateutil.parser.parse(exec_date) + timedelta(hours=9)

def get_executions(bf, afterId, beforeId, count):
  executions = []
  while True:
    try:
      executions = bf.fetch2(path='executions', api='public', method='GET', params={"product_code": SYMBOL_BTCFX, "after": afterId, "before": beforeId, "count": count})
      break
    except Exception as e:
      print("{}: API call error".format(datetime.now()))
      sleep(1)
  return executions

bf = ccxt.bitflyer()
dateSince = datetime(2018, 1, 29, 0, 0, 0)
# dateSince = datetime(2017, 12, 1, 0, 0, 0)
dateUntil = datetime(2018, 9, 11, 0, 0, 0)
count = 500
afterId = 124939529
beforeId = afterId + count + 1
handler = FileHandler('data/ohlcv/' + dateSince.strftime("%Y%m%d") + '.csv')
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
print("{}: Program start.".format(datetime.now()))

op, hi, lo, cl, vol = 0.0, 0.0, 0.0, 0.0, 0.0

exec_cnt = 0
loop = True
loop_cnt = 0
while loop:
  # 約定履歴を取得
  exs = get_executions(bf, afterId, beforeId, count)
  # たまに約定履歴がごっそりと無いことがある
  if(len(exs) == 0):
    print("no execs, ID count up: {} - {}, {}".format(afterId, beforeId, count))
    afterId += count
    beforeId += count
    continue
  afterId = exs[0]["id"]
  beforeId = afterId + count + 1
  date = get_exec_datetime(exs[-1])
  datePrev = date

  for ex in reversed(exs):
    date = get_exec_datetime(ex)
    if(dateSince <= date and date <= dateUntil):
      price = ex["price"]
      size = ex["size"]
      if(op == 0.0):
        op, hi, lo, cl, vol = price, price, price, price, size

      # 日付が変わったらファイルハンドラ変更
      if(date.day != datePrev.day):
        print("{}: {} finish, {} data. {} start, 1st id {}".format(datetime.now(), datePrev.strftime("%Y%m%d"), exec_cnt, date.strftime("%Y%m%d"), ex["id"]))
        handler.close()
        logger.removeHandler(handler)
        handler = FileHandler('data/ohlcv/' + date.strftime("%Y%m%d") + '.csv')
        handler.setLevel(INFO)
        logger.setLevel(INFO)
        logger.addHandler(handler)
        exec_cnt = 0

      # 秒が変わったらOHLCVリセット
      # ※ここをいじれば好きな解像度にできるはず、このコードは1秒足でデータ作成(抜けの補完はしてないので注意)
      if(date.second != datePrev.second or (date.minute != datePrev.minute and date.second == datePrev.second)):
        logger.info("{date},{op},{hi},{lo},{cl},{vol}".format(
          date=date.strftime("%Y-%m-%d %H:%M:%S"),
          op=int(op),
          hi=int(hi),
          lo=int(lo),
          cl=int(cl),
          vol=vol,
          )
        )
        op, hi, lo, cl, vol = price, price, price, price, size

      if(price > hi):
        hi = price
      if(price < lo):
        lo = price
      cl = price
      vol += size
      exec_cnt += 1

    if(date > dateUntil):
      loop = False
      print("{}: Collected all data, next ID {}".format(datetime.now(), ex["id"]))
      break
    datePrev = date

  # print("{}: loop end[{}]".format(loop_cnt+1, datetime.now()))
  # sleep(ITV_SLEEP)
  loop_cnt += 1
