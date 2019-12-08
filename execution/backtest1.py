import time
import ccxt
import sys
import json
import requests
from datetime import datetime
import numpy as np
import pandas as pd
from pandas import Series
import collections
import time

class VixCci:

    args = sys.argv
    df = pd.read_csv('board_{}.csv'.format(args[1]), header=None)
    high = np.array(df[0])
    low = np.array(df[1])
    close = np.array(df[2])
    date = np.array(df[3])
    np.set_printoptions(precision=4)  # print時に小数点以下4桁まで表示
    # print(low)
    # print(high)
    # print(close)

    # CM_Williams_Vix_Fix and Vix_Fix_inverse
    #upper/lowerBand:wvfのボリンジャーバンド
    #rangeHigh/Low:lb期間のwvf最大値
    def vixfix(self, close=close, low=low, high=high, period = 18,bbl = 20, mult = 0.5,lb = 50,ph = 0.85, pl=1.01):
        print('VixFix')
        period = period  # LookBack Period Standard Deviation High
        bbl = bbl  # Bolinger Band Length
        mult = mult  # Bollinger Band Standard Devaition Up
        lb = lb  # Look Back Period Percentile High
        ph = ph  # Highest Percentile - 0.90=90%, 0.95=95%, 0.99=99%
        pl = pl  # Lowest Percentile - 1.10=90%, 1.05=95%, 1.01=99%
        hp = False  # Show High Range - Based on Percentile and LookBack Period?
        sd = False  # Show Standard Deviation Line?
        # VixFix
        wvf = (pd.Series(close).rolling(period, 1).max() - low) / pd.Series(close).rolling(period, 1).max() * 100
        # VixFix_inverse
        wvf_inv = abs((pd.Series(close).rolling(period, 1).min() - high) / pd.Series(close).rolling(period,
                                                                                                   1).min() * 100)
        sDev = mult * pd.Series(wvf).rolling(bbl, 1).std()  # 期間bblでのVixFixの標準偏差
        midLine = pd.Series(wvf).rolling(bbl, 1).mean()  # 期間bblでのVixFixの単純移動平均
        lowerBand = midLine - sDev  # VixFixボリンジャーバンド(下)
        upperBand = midLine + sDev  # VixFixボリンジャーバンド(上)(水色)
        rangeHigh = pd.Series(wvf).rolling(lb, 1).max() * ph  # lb期間のwvf最大値
        rangeLow = pd.Series(wvf).rolling(lb, 1).min() * pl  # lb期間のwvf最小値
        result = collections.namedtuple('result', 'wvf, wvf_inv, lowerBand, upperBand, rangeHigh,rangeLow')
        return result(wvf=wvf,wvf_inv=wvf_inv,lowerBand=lowerBand,upperBand=upperBand,rangeHigh=rangeHigh,rangeLow=rangeLow)

    def cci(self, ndays, data=df):
         TP = (data[0] + data[1] + data[2]) / 3
         CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015 * TP.rolling(ndays).std()),
         name = 'CCI')
         data = data.join(CCI)
         return CCI.values

    def vix_signal_long(self, wvf, upperBand, rangeHigh):
        signal = []
        for i in range(0, len(wvf)-1):
            if wvf[i] >= upperBand[i] or wvf[i] >= rangeHigh[i]:
                signal.append(1)
            else:
                signal.append(0)
        return signal

    def cci_signal_long(self, tcci, ccis):
        signal = []
        signal.append(0)
        for i in range(1, len(tcci)-1):
            if ((tcci[i-1] < ccis[i-1] and tcci[i] > ccis[i]) and ccis[i-1] <= -61.8) or (ccis[i-1] < 0 and ccis[i] > 0):
                signal.append(1)
            else:
                signal.append(0)
        return signal

    def vix_signal_short(self, wvf_inv, lowerBand, rangeLow):
        signal = []
        for i in range(0, len(wvf)-1):
            if wvf_inv[i] <= lowerBand[i] or wvf_inv[i] <= rangeLow[i]:
                signal.append(-1)
            else:
                signal.append(0)
        return signal

    def cci_signal_short(self, tcci, ccis):
        signal = []
        signal.append(0)
        for i in range(1, len(tcci)-1):
            if ((tcci[i-1] > ccis[i-1] and tcci[i] < ccis[i]) and ccis[i-1] >= 61.8) or (ccis[i-1] > 0 and ccis[i] < 0):
                signal.append(-1)
            else:
                signal.append(0)
        return signal

    def signal_long(self, vix_signal_long, cci_signal_long):
        signal_long = []
        for i in range(0, len(vix_signal_long)):
            if vix_signal_long[i]==1 and cci_signal_long[i]==1:
                signal_long.append(1)
            else:
                signal_long.append(0)
        return signal_long

    def signal_short(self, vix_signal_short, cci_signal_short):
        signal_short = []
        for i in range(0, len(vix_signal_short)):
            if vix_signal_short[i]==-1 and cci_signal_short[i]==-1:
                signal_short.append(1)
            else:
                signal_short.append(0)
        return signal_short

    def signal_long_close(self, tcci, ccis, vix_short):
        signal_long_close = []
        signal_long_close.append(0)
        signal_long_close.append(0)
        for i in range(2, len(tcci)-1):
            if (tcci[i-1] > tcci[i-2] and tcci[i] < tcci[i-1] and tcci[i-1] >= 100) or (tcci[i] >= 195) or (ccis[i] >= 280) or vix_short[i]:
                signal_long_close.append(1)
            else:
                signal_long_close.append(0)
        return signal_long_close

    def signal_short_close(self, tcci, ccis, vix):
        signal_short_close = []
        signal_short_close.append(0)
        signal_short_close.append(0)
        for i in range(2, len(tcci)-1):
            if (tcci[i-1] < tcci[i-2] and tcci[i] > tcci[i-1] and tcci[i-1] <= -100) or (tcci[i] <= -195) or (ccis[i] <= -280) or vix[i]:
                signal_short_close.append(1)
            else:
                signal_short_close.append(0)
        return signal_short_close



vix = VixCci()
wvf, wvf_inv, lowerBand, upperBand, rangeHigh, rangeLow = vix.vixfix()
wvf = wvf.values
upperBand = upperBand.values
rangeHigh = rangeHigh.values

ccis = vix.cci(ndays=13)
tcci = vix.cci(ndays=5)

vix_signal_long = vix.vix_signal_long(wvf=wvf, upperBand=upperBand, rangeHigh=rangeHigh)
cci_signal_long = vix.cci_signal_long(tcci=tcci, ccis=ccis)

vix_signal_short = vix.vix_signal_short(wvf_inv=wvf_inv, lowerBand=lowerBand, rangeLow=rangeLow)
cci_signal_short = vix.cci_signal_short(tcci=tcci, ccis=ccis)

signal_long = vix.signal_long(vix_signal_long=vix_signal_long, cci_signal_long=cci_signal_long)
signal_long_close = vix.signal_long_close(tcci=tcci,ccis=ccis, vix_short=vix_signal_short)

signal_short = vix.signal_short(vix_signal_short=vix_signal_short, cci_signal_short=cci_signal_short)
signal_short_close = vix.signal_short_close(tcci=tcci,ccis=ccis, vix=vix_signal_long)

data = vix.df[2]
data = np.array(data)

def judge_vix(signal_long, signal_long_close, signal_short, signal_short_close):
    judge = [0] * len(signal_long)
    num = 0
    for i in range(len(signal_long)-1):
        if signal_long[i] == 1:
            num += -1
            judge[i] += -1
            i += 1
        elif signal_short[i] == 1:
            num += 1
            judge[i] += 1
            i += 1

        elif num > 0:
            if signal_long_close[i] == 1 or signal_short[i] == 1:
                judge[i] += -num
                num = 0
        elif num < 0:
            if signal_short_close[i] == 1 or signal_long[i] == 1:
                judge[i] += -num
                num = 0
    return judge

#日本円初期保有量
capital = 10000
total = capital
#取引単位（BTC）
units = 0.1

#買いポジを持っているときは1，売りポジを持っているときは-1，ポジを持っていないときは0
position = 0
number_of_trade = 0
judge = judge_vix(signal_long, signal_long_close, signal_short, signal_short_close)
total1 = []

#バックテスト．ローソク足の終値で取引すると仮定．最後のローソク足で全てのポジションを決済する．
for i in range(len(data)-1):
    if  judge[i] > 0:
        total = total - units * judge[i] * data[i]
        total1.append(total)
        position += judge[i]
        number_of_trade += 1
    elif judge[i] < 0:
        total = total + units * (-judge[i]) * data[i]
        total1.append(total)
        position += judge[i]
        number_of_trade += 1
    else:
        pass
#最後の足でポジションをまとめて決済．
if position > 0:#買いポジを最後に持っていたら売り決済
    total = total + units * position * data[-1]
    total1.append(total)
    position += -1
    number_of_trade += 1
elif position < 0:#売りポジを最後に持っていたら買い決済
    total = total - units * (-position) * data[-1]
    total1.append(total)
    position += 1
    number_of_trade += 1
print("Trade unit: {}".format(units))
print("The position code is {} now.".format(position))
print("Total P/L per day: {}".format(total-capital))
print("The number of trade: {}".format(number_of_trade))
# print(total1)
