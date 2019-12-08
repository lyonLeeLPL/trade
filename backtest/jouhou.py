# coding:utf-8
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
from statistics import mean, median,variance,stdev
import csv
import matplotlib.pyplot as plt

class VixCci:

    df = pd.read_csv('data/ohlcv/20180826.csv', header=None)
    high = np.array(df[2])
    low = np.array(df[3])
    close = np.array(df[4])
    np.set_printoptions(precision=4)  # print時に小数点以下4桁まで表示
    # print(low)
    # print(high)
    # print(close)

    # CM_Williams_Vix_Fix and Vix_Fix_inverse
    #upper/lowerBand:wvfのボリンジャーバンド
    #rangeHigh/Low:lb期間のwvf最大値
    def vixfix(self, close=close, low=low, high=high, period = 18,bbl = 20, mult = 0,lb = 15,ph = 0.85, pl=1.01):
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

    def vix_signal_short(self, wvf, upperBand, rangeHigh):
        signal = []
        for i in range(0, len(wvf)-1):
            if wvf[i] >= upperBand[i] or wvf[i] >= rangeHigh[i]:
                signal.append(1)
            else:
                signal.append(0)
        return signal

    def vix_signal_long(self, wvf_inv, lowerBand, rangeLow):
        signal = []
        for i in range(0, len(wvf)-1):
            if wvf_inv[i] <= lowerBand[i] or wvf_inv[i] <= rangeLow[i]:
                signal.append(1)
            else:
                signal.append(0)
        return signal

vix = VixCci()
wvf, wvf_inv, lowerBand, upperBand, rangeHigh, rangeLow = vix.vixfix()

# ccis = vix.cci(ndays=13)
# tcci = vix.cci(ndays=5)

vix_signal_short = vix.vix_signal_short(wvf, upperBand, rangeHigh)
# cci_signal_long = vix.cci_signal_long(tcci, ccis)

vix_signal_long = vix.vix_signal_long(wvf_inv, lowerBand, rangeLow)
# cci_signal_short = vix.cci_signal_short(tcci, ccis)

# signal_long = vix.signal_long(vix_signal_long, cci_signal_long)
# signal_long_close = vix.signal_long_close(tcci,ccis, vix_signal_short)

# signal_short = vix.signal_short(vix_signal_short, cci_signal_short)
# signal_short_close = vix.signal_short_close(tcci,ccis, vix_signal_long)
# print(np.array(vix_signal_long) + np.array(vix_signal_short))

# with open('some.csv', 'w') as f:
#     writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
#     writer.writerow(np.array(vix_signal_long) + np.array(vix_signal_short))     # list（1次元配列）の場合
data = vix.df[4]
data = np.array(data)
high = vix.df[2]
low = vix.df[3]
op = vix.df[1]
# print(wvf)

def judge_vix(signal_long, signal_short, data=data):
    judge = [0] * len(signal_long)
    num = 0
    price = []
    sihyou = []
    sanpu = []
    price = data[0]
    k = 0
    for i in range(len(signal_long)-1):
        if signal_short[i] == 1:
            if num == 0:
                num += -1
                judge[i] += -1
            elif num > 0:
                judge[i] += -(num)
                num = -1
            price = data[i]
        elif signal_long[i] == 1:
            if num == 0:
                num += 1
                judge[i] += 1
            elif num < 0:
                judge[i] += -(num)
                num = 1
            price = data[i]
    return judge, price, sihyou, sanpu

#日本円初期保有量
capital = 10000
total = capital
#取引単位（BTC）
units = 0.1

#買いポジを持っているときは1，売りポジを持っているときは-1，ポジを持っていないときは0
position = 0
number_of_trade = 0
judge, price, sihyou, sanpu = judge_vix(vix_signal_long, vix_signal_short)
total1 = [10000]
total2 = []
sui = []
# sihyou.pop()
#バックテスト．ローソク足の終値で取引すると仮定．最後のローソク足で全てのポジションを決済する．
for i in range(len(data)-1):
    if  judge[i] > 0:
        total = total - units * judge[i] * (data[i])
        # total1.append(total)
        position += judge[i]
        number_of_trade += 1
    elif judge[i] < 0:
        total = total + units * (-judge[i]) * (data[i])
        # total1.append(total)
        position += judge[i]
        number_of_trade += 1
    else:
        pass
    if position == 0:
        total1.append(total)
position_max = max(judge)
position_min = min(judge)
#最後の足でポジションをまとめて決済．
if position > 0:#買いポジを最後に持っていたら売り決済
    total = total + units * position * data[-1]
    total1.append(total)
    position += -position
    number_of_trade += 1
elif position < 0:#売りポジを最後に持っていたら買い決済
    total = total - units * (-position) * data[-1]
    total1.append(total)
    position += -position
    number_of_trade += 1
print("Trade unit: {}".format(units))
print("The position code is {} now.".format(position))
print("Total P/L per day: {}".format(total-capital))
print("The number of trade: {}".format(number_of_trade))
print("position:max{}, min{}".format(position_max, position_min))
# print(price)
plt.plot(total1)
plt.show()

# x = np.array(sihyou)
# y = np.array(sanpu)
# # a, b = np.polyfit(x, y, 1)
# # # フィッティング直線
# # y2 = a * x + b
#
# fig=plt.figure()
# ax=fig.add_subplot(111)
# ax.scatter(x,y,alpha=0.5,color="Blue",linewidths="1")
# # ax.plot(x, y2,color='black')
# # ax.text(0.1,a*0.1+b, 'y='+ str(round(a,4)) +'x+'+str(round(b,4)))
# plt.show()
