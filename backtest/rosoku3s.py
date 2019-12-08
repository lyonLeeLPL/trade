import pandas as pd
from datetime import datetime

DATA_DIR = 'data/ohlcv/'
SINCE = datetime(2018, 8, 24)
UNTIL = datetime(2018, 8, 27)
RES_NUM = 60 # 解像度
RES_UNIT = "s" # 解像度
RES_SEC = RES_NUM * (1 if RES_UNIT == "s" else 60 if RES_UNIT == "m" else 60*60)

# Pandas Dataframe
inCsvPath = DATA_DIR + SINCE.strftime("%Y%m%d") + ".csv"
df = pd.read_csv(inCsvPath, header=None, names=["T", "O", "H", "L", "C", "V"], parse_dates=["T"])

# 出力ファイル
outCsvPath = DATA_DIR + SINCE.strftime("%Y%m%d") + "_" + str(RES_NUM) + RES_UNIT + ".csv"
outCsv = open(outCsvPath, mode="w")

# 解像度範囲
rangeS = datetime.fromtimestamp(SINCE.timestamp())
rangeE = datetime.fromtimestamp(rangeS.timestamp() + RES_SEC)

# 終了日時までループ
while rangeE <= UNTIL:
  df_ = df.query('@rangeS <= T & T < @rangeE')
  if(not(df_.empty)):
    outCsv.write("{t},{o},{h},{l},{c},{v}\n".format(
      t=rangeS.strftime("%Y-%m-%d %H:%M:%S"),
      o=df_['O'].iloc[0],
      h=df_['H'].max(),
      l=df_['L'].min(),
      c=df_['C'].iloc[-1],
      v=df_['V'].sum(),
    ))

  # 日付変更(ファイル変更)
  if(rangeS.day != rangeE.day):
    print("{}: {} fin, next {}".format(datetime.now(), rangeS.strftime("%Y%m%d"), rangeE.strftime("%Y%m%d")))
    outCsv.close()

    # 入力ファイルがなければ終了
    inCsvPath = DATA_DIR + rangeE.strftime("%Y%m%d") + ".csv"
    try:
      df = pd.read_csv(inCsvPath, header=None, names=["T", "O", "H", "L", "C", "V"], parse_dates=["T"])
    except Exception as e:
      print(e)
      break

    # 新規出力ファイル
    outCsvPath = DATA_DIR + rangeE.strftime("%Y%m%d") + "_" + str(RES_NUM) + RES_UNIT + ".csv"
    outCsv = open(outCsvPath, mode="w")

  # 解像度範囲 更新
  rangeS = rangeE
  rangeE = datetime.fromtimestamp(rangeS.timestamp() + RES_SEC)

if(not(outCsv.closed)):
  outCsv.close()
