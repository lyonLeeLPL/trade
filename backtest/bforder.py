import pybitflyer
import json
import logging
import time
import datetime

#注文処理をまとめている
class BFOrder:
    def __init__(self):
        #config.jsonの読み込み
        f = open('config/config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.product_code = config["product_code"]
        self.key = config["key"]
        self.secret = config["secret"]
        self.api = pybitflyer.API(self.key, self.secret)

    def limit(self, side, price, size, minute_to_expire=None):
        logging.info("Order: Limit. Side : {}".format(side))
        response = {"status":"internalError in bforder.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
                break
            else:
                logging.debug(response)
            time.sleep(0.1)
        return response

    def market(self, side, size, minute_to_expire= None):
        logging.info("Order: Market. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        logging.info(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def ticker(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.ticker(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.ticker(product_code=self.product_code)
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def getexecutions(self, order_id):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
        except:
            pass
        logging.debug(response)
        retry = 0
        while ("status" in response or not response):
            try:
                response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
            except:
                pass
            retry += 1
            if retry > 500:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def getboard(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getboard(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.getboard(product_code=self.product_code)
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def getboardstate(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getboardstate(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.getboardstate(product_code=self.product_code)
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def stop(self, side, size, trigger_price, minute_to_expire=None):
        logging.info("Order: Stop. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,"trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        retry = 0
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,"trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
            except:
                pass
            retry += 1
            if retry > 20:
                logging.error(response)
            else:
                logging.debug(response)
            time.sleep(0.5)
        return response

    def stop_limit(self, side, size, trigger_price, price, minute_to_expire=None):
        logging.info("Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,"trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,"trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
            except:
                pass
            logging.debug(response)
        return response

    def trailing(self, side, size, offset, minute_to_expire=None):
        logging.info("Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size, "offset": offset, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size, "offset": offset, "minute_to_expire": minute_to_expire}])
            except:
                pass
            logging.debug(response)
        return response

    def getcollateral(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getcollateral()
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.getcollateral()
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response

    def cancelchildorder(self, orderId):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.cancelchildorder(product_code= self.product_code, child_order_acceptance_id = orderId)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.cancelchildorder(product_code = self.product_code, child_order_acceptance_id = orderId)
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response

    def cancelparentorder(self, orderId):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.cancelparentorder(product_code= self.product_code, parent_order_acceptance_id = orderId)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.cancelparentorder(product_code = self.product_code, parent_order_acceptance_id = orderId)
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response

    def getchildorders(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getchildorders(product_code= self.product_code, child_order_state = "ACTIVE")
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.getchildorders(product_code = self.product_code, child_order_state = "ACTIVE")
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response

    def getparentorders(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getparentorders(product_code= self.product_code, parent_order_state = "ACTIVE")
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.getparentorders(product_code = self.product_code, parent_order_state = "ACTIVE")
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response

    def parentorderId(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getparentorders(product_code= self.product_code, parent_order_state = "COMPLETED")
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.getparentorders(product_code= self.product_code, parent_order_state = "COMPLETED")
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        id = [d["parent_order_acceptance_id"] for d in response]
        return id


    def getpositions(self):
        side = ""
        size = 0
        poss = self.api.getpositions(product_code = self.product_code)

        #もしポジションがあれば合計値を取得
        if len(poss) != 0:
            for pos in poss:
                side = pos["side"]
                size += pos["size"]
        else:
            side = 'none'
            size = 0
        return side,size

    def cancelallchildorders(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.cancelallchildorders(product_code= self.product_code)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.cancelallchildorders(product_code = self.product_code)
            except:
                pass
            logging.info(response)
            time.sleep(0.5)
        return response
