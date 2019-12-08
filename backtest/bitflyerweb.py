import time
import datetime
from selenium import webdriver
import random
import json
from time import sleep
from bs4 import BeautifulSoup as bs
import re
import threading
import requests
import logging
import ast
import datetime

class BitflyerWeb:
    def __init__(self):
        self.pjs_path = ''
        self.bf_sendorder_url = 'https://lightning.bitflyer.jp/api/trade/sendorder'
        self.user_id = 'taichi-8128@ezweb.ne.jp'
        self.user_password = 'wxY-dN3-GQk-ogE'
        self.account_id = ""
        self.session = ""
        self.best_ask = 0
        self.best_bid = 0
        self.last_price = 0
        self.driver_bitflyer = webdriver.PhantomJS()
        self.html = ""
        self.market_state = ""
        self.bid_price = []
        self.bid_size = []
        self.ask_price = []
        self.ask_size = []
        self.execution_price = []
        self.execution_size = []
        self.execution_time = []
        self.spread = 0
        self.proxies = {
            'http':'http://proxy.-----.co.jp/proxy.pac',
            'https':'http://proxy.-----.co.jp/proxy.pac'
            }
        self.driver_inago = webdriver.PhantomJS()
        self.driver_inago.get("https://inagoflyer.appspot.com/btcmac")

    def login(self):
        self.driver_bitflyer.get('https://lightning.bitflyer.jp')
        loginid = self.driver_bitflyer.find_element_by_id('LoginId')
        password = self.driver_bitflyer.find_element_by_id('Password')
        loginid.send_keys(self.user_id)
        password.send_keys(self.user_password)
        self.driver_bitflyer.find_element_by_id('login_btn').click()
        self.driver_bitflyer.implicitly_wait(3)
        self.account_id = self.driver_bitflyer.find_element_by_xpath("//body").get_attribute('data-account')
        account_id = self.driver_bitflyer.find_element_by_xpath("//body").get_attribute('data-account')
        # print("confirmation code:")
        # code = input()
        # confirmation_code = self.driver_bitflyer.find_element_by_name("ConfirmationCode")
        # confirmation_code.send_keys(code)
        # self.driver_bitflyer.find_element_by_xpath("//button[@class='button raised clickable']").click()

        cookies = self.driver_bitflyer.get_cookies()

        for c in cookies:
            if "name" in c and c['name'] == "api_session_v2":
                self.session = c['value']
        if self.session == "":
            print("session failed")

        #関数VOLでボリュームをスクレイプ
    def inago(self):
    	for buyvol in self.driver_inago.find_elements_by_id("buyVolumePerMeasurementTime"):
    		buy = buyvol.text
    	for sellvol in self.driver_inago.find_elements_by_id("sellVolumePerMeasurementTime"):
    		sell = sellvol.text
    	return buy,sell


    # def getDataWeb(self):
    #     self.login()
    #     while True:
            # self.html = bs(self.driver_bitflyer.page_source.encode("utf-8"))
            # execution = self.html.find_all('ul', attrs={'class': "market-history__list"})[0]
            # self.execution_price = re.findall(r'\d+', str(execution.find_all('span', attrs={'class': "market-history__price"})))
            # self.execution_size = [i[0] if re.match(r"\d+\.$" , i) else i for i in re.findall(r'\d+\.\d+|\d+\.', str(execution.find_all('span', attrs={'class': "market-history__size"})))]
            # self.execution_time = re.findall(r'\d+:\d+:\d+', str(execution.find_all('span', attrs={'class': "market-history__time"})))
            # self.spread = self.html.find_all('span', attrs={'class': "spreadperc-value"})[0].text[:-1]
            # self.bid_price = re.findall(r'\d+', str(self.html.find_all('ul', attrs={'class': "bid__inner"})[0].find_all('span', attrs={'class': "orderbook__price"})))
            # self.bid_size = [i[0] if re.match(r"\d+\.$" , i) else i for i in re.findall(r'\d+\.\d+|\d+\.', str(self.html.find_all('ul', attrs={'class': "bid__inner"})[0].find_all('span', attrs={'class': "orderbook__size"})))]
            # self.ask_price = re.findall(r'\d+', str(self.html.find_all('ul', attrs={'class': "offer__inner"})[0].find_all('span', attrs={'class': "orderbook__price"})))
            # self.ask_size = [i[0] if re.match(r"\d+\.$" , i) else i for i in re.findall(r'\d+\.\d+|\d+\.', str(self.html.find_all('ul', attrs={'class': "offer__inner"})[0].find_all('span', attrs={'class': "orderbook__size"})))]
    #         self.best_ask = self.html.find_all('span', attrs={'class': 'advanced__ticker-item advanced__ticker-item--ask'})[0].text.split()[2]
    #         self.best_bid = self.html.find_all('span', attrs={'class': 'advanced__ticker-item advanced__ticker-item--bid'})[0].text.split()[2]
    #         self.last_price = self.html.find_all('span', attrs={'class': 'advanced__ticker-item advanced__ticker-item--ltp'})[0].text.split()[1]
    #         self.market_state = re.search(r'title="(.+)"', str(self.html.find_all('span', attrs={'class': "market-state"}))).group(1)

    # def print_loop(self):
    #     while True:
    #         # print("{}.{},{},{}".format(self.best_ask, self.best_bid, self.last_price, self.market_state))
    #         print("{}.{},{},{}".format(self.bid_price, self.bid_size, self.ask_price, self.ask_size))
    #         # print("{}.{},{},{}".format(self.execution_price, self.execution_size, self.execution_time, self.spread))
    #         sleep(0.5)

    def orderMarket(self, side, size):
        r = requests.post(self.bf_sendorder_url, data= json.dumps({'account_id': self.account_id, 'is_check': 'false', 'lang': 'ja', 'minuteToExpire': '43200', 'ord_type': 'MARKET', 'order_ref_id': datetime.datetime.now().strftime("JRF%Y%m%d-%H%M%S-") + '{0:06d}'.format(random.randint(0,999999)), 'price': '0', 'product_code': 'FX_BTC_JPY', 'side': side, 'size': size, 'time_in_force': 'GTC'}), headers = {'Content-Type': 'application/json; charset=utf-8', 'Cookie': 'api_session_v2='+self.session, 'X-Requested-With':'XMLHttpRequest'})
        print(r.text)

    def orderLimit(self, price, side, size):
        logging.info("Order: Limit. Side : {}".format(side))
        response = {"status":"internalError in bforder.py"}
        try:
            response = requests.post(self.bf_sendorder_url, data=json.dumps({'account_id': self.account_id, 'is_check': 'false', 'lang': 'ja', 'minuteToExpire': '43200', 'ord_type': 'LIMIT', 'order_ref_id': datetime.datetime.now().strftime("JRF%Y%m%d-%H%M%S-") + '{0:06d}'.format(random.randint(0,999999)), 'price': price, 'product_code': 'FX_BTC_JPY', 'side': side, 'size': size, 'time_in_force': 'GTC'}), headers = {'Content-Type': 'application/json; charset=utf-8', 'Cookie': 'api_session_v2='+self.session, 'X-Requested-With':'XMLHttpRequest'})
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = requests.post(self.bf_sendorder_url, data= json.dumps({'account_id': self.account_id, 'is_check': 'false', 'lang': 'ja', 'minuteToExpire': '43200', 'ord_type': 'LIMIT', 'order_ref_id': datetime.datetime.now().strftime("JRF%Y%m%d-%H%M%S-") + '{0:06d}'.format(random.randint(0,999999)), 'price': price, 'product_code': 'FX_BTC_JPY', 'side': side, 'size': size, 'time_in_force': 'GTC'}), headers = {'Content-Type': 'application/json; charset=utf-8', 'Cookie': 'api_session_v2='+self.session, 'X-Requested-With':'XMLHttpRequest'})
            except:
                pass
            retry += 1
            if retry > 10:
                logging.error(response)
                break
            else:
                logging.debug(response)
            time.sleep(0.1)
        json_acceptable_string = response.text.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        print(d)
        r = d['data']['order_ref_id']
        print(r)
        return r

if __name__ == '__main__':
    BF = BitflyerWeb()
    # BF.orderMarket("BUY")
    # BF.login()
    # while True:
    #     buy, sell = BF.inago()
    #     print(buy)
    #     print(sell)
    #     print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    #     print("============================")
    #     time.sleep(1)
    # BF.orderLimit(600000, "BUY")
    # thread_1 = threading.Thread(target=BF.html_data)
    # thread_2 = threading.Thread(target=BF.bestPriceWeb)
    # thread_3 = threading.Thread(target=BF.boardWeb)
    # thread_4 = threading.Thread(target=BF.getDataWeb)

    # thread_1.start()
    # thread_2.start()
    # thread_3.start()
    # thread_4.start()
