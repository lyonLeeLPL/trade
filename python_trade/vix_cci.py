# coding: UTF-8
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
import CryptoWatch
import Pybitflyer
import time

class VixCci:

    # CM_Williams_Vix_Fix and Vix_Fix_inverse
    #rangeHigh/Low:lb期間のwvf最大値
    def vixfix(self, close, low, high, period = 18,bbl = 20, mult = 0.5,lb = 50,ph = 0.85, pl=1.01):
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

    def cci(self, ndays, data):
         TP = (data[2] + data[3] + data[4]) / 3
         CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015 * TP.rolling(ndays).std()),
         name = 'CCI')
         data = data.join(CCI)
         return CCI.values

    def vix_signal_long(self, wvf, upperBand, rangeHigh):
        signal = 0
        if wvf >= upperBand or wvf >= rangeHigh:
            signal = 1
        else:
            signal = 0
        return signal

    def cci_signal_long(self, tcci, ccis):
        signal = 0
        if ((tcci[0] < ccis[0] and tcci[1] > ccis[1]) and ccis[0] <= -61.8) or (ccis[0] < 0 and ccis[1] > 0):
            signal = 1
        else:
            signal = 0
        return signal

    def vix_signal_short(self, wvf_inv, lowerBand, rangeLow):
        signal = 0
        if wvf_inv <= lowerBand or wvf_inv <= rangeLow:
            signal = -1
        else:
            signal = 0
        return signal

    def cci_signal_short(self, tcci, ccis):
        signal = 0
        if ((tcci[0] > ccis[0] and tcci[1] < ccis[1]) and ccis[0] >= 61.8) or (ccis[0] > 0 and ccis[1] < 0):
            signal = -1
        else:
            signal = 0
        return signal

    def signal_long(self, vix_signal_long, cci_signal_long):
        signal_long = 0
        if vix_signal_long==1 and cci_signal_long==1:
            signal_long = 1
        else:
            signal_long = 0
        return signal_long

    def signal_short(self, vix_signal_short, cci_signal_short):
        signal_short = 0
        if vix_signal_short==-1 and cci_signal_short==-1:
            signal_short = 1
        else:
            signal_short = 0
        return signal_short

    def signal_long_close(self, tcci, ccis, vix_short):
        signal_long_close = 0
        if (tcci[1] > tcci[0] and tcci[2] < tcci[1] and tcci[1] >= 100) or (tcci[2] >= 195) or (ccis[2] >= 280) or vix_short == -1:
            signal_long_close = 1
        else:
            signal_long_close = 0
        return signal_long_close

    def signal_short_close(self, tcci, ccis, vix):
        signal_short_close = 0
        if (tcci[1] < tcci[0] and tcci[2] > tcci[1] and tcci[1] <= -100) or (tcci[2] <= -195) or (ccis[2] <= -280) or vix== 1:
            signal_short_close = 1
        else:
            signal_short_close = 0
        return signal_short_close


pos = 0
while True:
    vix = VixCci()
    df = pd.read_csv('data/ohlcv/test.csv', header=None)
    high = np.array(df[2][-25:])
    low = np.array(df[3][-25:])
    close = np.array(df[4][-25:])
    print(df[-1:])
    np.set_printoptions(precision=4)  # print時に小数点以下4桁まで表示
    wvf, wvf_inv, lowerBand, upperBand, rangeHigh, rangeLow = vix.vixfix(close=close, low=low, high=high)
    wvf = wvf.values
    wvf_inv = wvf_inv.values
    lowerBand = lowerBand.values
    upperBand = upperBand.values
    rangeHigh = rangeHigh.values
    rangeLow = rangeLow.values


    ccis = vix.cci(ndays=13,data=df[-25:])
    tcci = vix.cci(ndays=5,data=df[-25:])

    vix_signal_long = vix.vix_signal_long(wvf=wvf[-1], upperBand=upperBand[-1], rangeHigh=rangeHigh[-1])
    cci_signal_long = vix.cci_signal_long(tcci=tcci[-2:], ccis=ccis[-2:])

    vix_signal_short = vix.vix_signal_short(wvf_inv=wvf_inv[-1], lowerBand=lowerBand[-1], rangeLow=rangeLow[-1])
    cci_signal_short = vix.cci_signal_short(tcci=tcci[-2:], ccis=ccis[-2:])

    signal_long = vix.signal_long(vix_signal_long=vix_signal_long, cci_signal_long=cci_signal_long)
    signal_long_close = vix.signal_long_close(tcci=tcci[-3:],ccis=ccis[-3:], vix_short=vix_signal_short)

    signal_short = vix.signal_short(vix_signal_short=vix_signal_short, cci_signal_short=cci_signal_short)
    signal_short_close = vix.signal_short_close(tcci=tcci[-3:],ccis=ccis[-3:], vix=vix_signal_long)

    trade = Pybitflyer.Pybitflyer()


    if signal_long == 1:
        trade.limit(side='SELL',size=0.01,price=df[4][-1:])
        print("sell")
        pos += -0.01
    elif signal_short == 1:
        trade.limit(side='BUY',size=0.01,price=df[4][-1:])
        print("buy")
        pos += 0.01
    elif pos > 0:
        if signal_long_close == 1 or signal_short == 1:
            trade.limit(side='SELL',size=pos,price=df[4][-1:])
            print("sell kessai")
            pos = 0
    elif pos < 0:
        if signal_short_close == 1 or signal_long == 1:
            trade.limit(side='BUY',size=pos,price=df[4][-1:])
            print("buy kessai")
            pos = 0
    else:
        trade.cancelAllorder()
    time.sleep(1)
