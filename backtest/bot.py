import time
import ccxt
import sys
import json
import requests
import datetime
import numpy as np
import pandas as pd
from pandas import Series
import collections
import time
from collections import deque
import bforder
import logging
import websocket
import math
import threading
import csv
import threading
import py_bitflyer_jsonrpc
import bitflyerweb
import traceback
import random

# ログの出力名を設定（1）
logger = logging.getLogger('LoggingTest')
# ログレベルの設定（2）
logger.setLevel(10)

class VIX:
    # CM_Williams_Vix_Fix and Vix_Fix_inverse
    #upper/lowerBand:wvfのボリンジャーバンド
    #rangeHigh/Low:lb期間のwvf最大値
    def vixfix(self, close, low, high, period = 1, bbl = 1, mult = 0, lb = 15, ph = 0.85, pl=1.15):
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
        rangeLow = pd.Series(wvf_inv).rolling(lb, 1).min() * pl  # lb期間のwvf最小値
        return wvf.values[-1],wvf_inv.values[-1],lowerBand.values[-1],upperBand.values[-1],rangeHigh.values[-1],rangeLow.values[-1]

    def vix_signal_short(self, wvf, upperBand, rangeHigh):
        signal = 0
        if wvf >= upperBand or wvf >= rangeHigh:
            signal = 1
        else:
            signal = 0
        return signal

    def vix_signal_long(self, wvf_inv, lowerBand, rangeLow):
        signal = 0
        if wvf_inv <= lowerBand or wvf_inv <= rangeLow:
            signal = 1
        else:
            signal = 0
        return signal

class Trade:
    def __init__(self):
        #config.jsonの読み込み
        f = open('config/config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self._executions = []
        self.executions_pre = []
        self._spotExecutions = deque(maxlen=300)
        self._boards = deque(maxlen=300)
        self.rpcFX = py_bitflyer_jsonrpc.BitflyerJSON_RPC(symbol='FX_BTC_JPY')
        self.rpcBTC = py_bitflyer_jsonrpc.BitflyerJSON_RPC(symbol='BTC_JPY')
        self.best_bid = 0
        self.best_ask = 0
        self._product_code = config["product_code"]
        self.orderId = []
        self.orderId_ri = []
        self.position = 0
        self.mid_price = 0
        self.order = bforder.BFOrder()
        #取引所のヘルスチェック
        self.healthCheck = config["healthCheck"]
        # 現物とFXの価格差がSFDの許容値を超えた場合にエントリーを制限
        self.sfdLimit = True
        self.high = deque(maxlen=30)
        self.low = deque(maxlen=30)
        self.close = deque(maxlen=30)
        self.judgement = deque(maxlen=30)
        self.vix = VIX()
        self.BitflyerWeb = bitflyerweb.BitflyerWeb()

    @property
    def boards(self):
        return self._boards
    @boards.setter
    def boards(self, val):
        self._boards = val

    @property
    def executions(self):
        return self._executions
    @executions.setter
    def executions(self, val):
        self._executions = val

    @property
    def spotExecutions(self):
        return self._spotExecutions
    @spotExecutions.setter
    def spotExecutions(self, val):
        self._spotExecutions = val

    @property
    def product_code(self):
        return self._product_code
    @product_code.setter
    def product_code(self, val):
        self._product_code = val

    def sfd(self):
        try:
            #現物とFXの乖離率を計算
            sfdPosition = 0
            if self.sfdLimit == True:
                if self.executions[-1]["price"] > self.spotExecutions[-1]["price"]:
                    sfd = round(self.executions[-1]["price"] / self.spotExecutions[-1]["price"] * 100 - 100,3)
                    if sfd > 4.9:
                        logger.info("Long limitation SFD:%s",sfd)
                        sfdPosition = 1
                else:
                    sfd = round(self.spotExecutions[-1]["price"] / self.executions[-1]["price"] * 100 - 100,3)
                    if sfd > 4.9:
                        logger.info("Short limitation SFD:%s",sfd)
                        sfdPosition = -1
                if sfd <= 4.9:
                    logger.info("SFD:%s",sfd)
        except:
            logger.error("sfderror")

    def health(self):
        #取引所のヘルスチェック
        try:
            boardState = self.order.getboardstate()
            serverHealth = True
            permitHealth1 = ["NORMAL", "BUSY", "VERY BUSY"]
            permitHealth2 = ["NORMAL", "BUSY", "VERY BUSY", "SUPER BUSY"]
            if (boardState["health"] in permitHealth1) and boardState["state"] == "RUNNING" and self.healthCheck:
                pass
            elif (boardState["health"] in permitHealth2) and boardState["state"] == "RUNNING" and not self.healthCheck:
                pass
            else:
                serverHealth = False
                logger.info('Server is %s/%s. Do not order.', boardState["health"], boardState["state"])
            return serverHealth
        except:
            serverHealth = False
            logger.error("Health check failed")

    def judge(self):
        # logger.info("calJudge")
        #close, high, lowをデータフレーム化
        wvf, wvf_inv, lowerBand, upperBand, rangeHigh, rangeLow = self.vix.vixfix(self.close, self.low, self.high)
        vix_signal_short = self.vix.vix_signal_short(wvf, upperBand, rangeHigh)
        vix_signal_long = self.vix.vix_signal_long(wvf, lowerBand, rangeLow)
        if vix_signal_short == 1:
            return -1
        elif vix_signal_long == 1:
            return 1
        else:
            return 0

    def loop(self):
        """
        注文の実行ループを回す関数
        """
        while True:
            try :
                logger.info('================================')
                print(self.orderId)
                print(self.orderId_ri)
                print(self.position)
                self.collectExecution()

                judge = self.judge()
                if random.randrange(5) == 2:
                    self.positioncheck()
                pos = round(self.position, 6)

                if self.health:
                    #ロングエントリー
                    if judge == 1:
                        #引数で売り買い判断
                        if pos == 0 and len(self.orderId_ri) == 0 and len(self.orderId) < 1:
                            logger.info("ロングエントリー")
                            self.orderId.append([self.BitflyerWeb.orderLimit(self.close[-1], "BUY", 0.01), 1, 0])
                            time.sleep(0.8)
                        elif pos < 0 and len(self.orderId_ri) == 0:
                            logger.info("ショートクローズ")
                            self.orderId_ri.append([self.BitflyerWeb.orderLimit(self.close[-1], "BUY", -pos), 2, 0])
                            time.sleep(0.8)
                        else:
                            time.sleep(1)
                    #ショートエントリー
                    elif judge == -1:
                        if pos == 0 and len(self.orderId_ri) == 0 and len(self.orderId) < 1:
                            logger.info("ショートエントリー")
                            self.orderId.append([self.BitflyerWeb.orderLimit(self.close[-1], "SELL", 0.01), -1, 0])
                            time.sleep(0.8)
                        elif pos > 0 and len(self.orderId_ri) == 0:
                            logger.info("ロングクローズ")
                            self.orderId_ri.append([self.BitflyerWeb.orderLimit(self.close[-1], "SELL", pos), -2, 0])
                            time.sleep(0.8)
                        else:
                            time.sleep(1)
                    else:
                        time.sleep(1)
            except:
                logger.info("loopエラー")


    # def kessai(self):
    #     try:
    #         side = ""
    #         size = self.position
    #         if size > 0:
    #             side = "SELL"
    #         elif size < 0:
    #             side = "BUY"
    #         self.BitflyerWeb.orderMarket(side)
    #     except:
    #         logger.error("kessai2エラー")

    #約定しているかチェック
    def checkOrder(self):
        while True:
            try:
                if len(self.orderId) > 0:
                    for i in self.orderId[:]:
                        #約定していたら
                        if self.rpcFX.get_execution(i[0]):
                            self.orderId.remove(i)
                            logger.info("エントリーが約定しました {}".format(i[0]))
                            if i[1] == 1:
                                self.position += 0.01
                            elif i[1] == -1:
                                self.position += -0.01
                        else:
                            i[2] += 1
                            if i[2] > 3:
                                logger.info("約定されませんでした。キャンセルします。 {}".format(i[0]))
                                self.order.cancelchildorder(i[0])
                                self.orderId.remove(i)

                if len(self.orderId_ri) > 0:
                    for i in self.orderId_ri[:]:
                        #約定していたら
                        if self.rpcFX.get_execution(i[0]):
                            self.orderId_ri.remove(i)
                            logger.info("エントリーをcloseしました {}".format(i[0]))
                            if i[1] == 2:
                                self.position += -self.position
                            elif i[1] == -2:
                                self.position += -self.position
                        else:
                            i[2] += 1
                            if i[2] > 3:
                                logger.info("close注文が約定されませんでした。指し直します。{}".format(i[0]))
                                self.order.cancelchildorder(i[0])
                                self.orderId_ri.remove(i)
                                if i[1] == 2:
                                    self.orderId_ri.append([self.BitflyerWeb.orderLimit(self.close[-1], "BUY", round(-self.position, 6)), 2, 0])
                                elif i[1] == -2:
                                    self.orderId_ri.append([self.BitflyerWeb.orderLimit(self.close[-1], "SELL", round(self.position, 6)), -2, 0])
                time.sleep(0.8)
            except:
                logger.error("checkOrderエラー")


    def tyumon(self):
        while True:
            try:
                if self.BitflyerWeb.driver_bitflyer.current_url != "https://lightning.bitflyer.jp/trade":
                    self.BitflyerWeb.login()
                #注文を持っている時
                self.ordernum = len(self.order.getchildorders())
                orders = self.order.getchildorders()
                if self.ordernum > 0:
                    for o in orders:
                        id = o["child_order_acceptance_id"]
                        l_in = [s for s in self.orderId if id == s[0]]
                        if len(l_in) == 0:
                            self.order.cancelchildorder(id)
                            logger.info("予期せぬ注文があったのでキャンセルします。")
                else:
                    self.orderli = 0
                time.sleep(1)
            except:
                logger.error("tyumonエラー")

    def positioncheck(self):
        # while True:
        try:
            pos_side, pos_size = self.order.getpositions()
            if pos_side == "BUY":
                self.position = pos_size
            elif pos_side == "SELL":
                self.position = -pos_size
            if pos_size > 0:
                #0.01以下のポジションを持っていた場合現在のポジションを0とする
                if pos_size < 0.01 and len(self.order.getchildorders()) == 0:
                    self.position = 0
                #もし現在ポジションを持っていなければ全てクリアする。
            if self.position == 0:
                self.orderId.clear()
                self.order.cancelallchildorders()
                logger.info('ポジションをクリアしました。')
            # if len(self.orderId) == 0:
            #     self.position = 0
            time.sleep(1)
        except:
            logger.error("positioncheckエラー")

    def collectExecution(self):
        try:
            self.executions = self.rpcFX.get_execution()
            self.spotExecutions = self.rpcBTC.get_execution()
            new = []
            if len(self.executions_pre) > 0:
                for i in self.executions[::-1]:
                    #新しい約定履歴を取得（exec_dateを参照している）
                    if float(i['exec_date'][11:22].replace(':', '')) > float(self.executions_pre[-1]['exec_date'][11:22].replace(':', '')):
                        new.append(i)
                    else:
                        break
            self.executions_pre = self.executions[:]
            price_list = [i["price"] for i in reversed(new)]
            if len(new) > 0:
                self.high.append(max(price_list))
                self.low.append(min(price_list))
                self.close.append(price_list[-1])
        except:
            logger.error("collectExecutionエラー")
            traceback.print_exc()


if __name__ == '__main__':
    Trade = Trade()
    Trade.BitflyerWeb.login()
    thread_1 = threading.Thread(target=Trade.loop)
    # thread_2 = threading.Thread(target=Trade.collectExecution)
    thread_3 = threading.Thread(target=Trade.checkOrder)
    # thread_4 = threading.Thread(target=Trade.positioncheck)
    thread_5 = threading.Thread(target=Trade.tyumon)
    thread_1.start()
    # thread_2.start()
    thread_3.start()
    # thread_4.start()
    thread_5.start()
    # VixCci.collectExecution()
    # VixCci.getBorad()
