# coding: UTF-8
class Pybitflyer:
    import pybitflyer

    API_KEY = 'API KEY'
    API_SECRET = 'API SECRET'
    API = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)
    SIZE = 0.01  #注文する量


    def market(self, side, size, minute_to_expire= None):
        print("Order: Market. Side : {}".format(side))
        response = {"status": "internalError in order.py"}
        try:
            response = self.API.sendchildorder(product_code = "FX_BTC_JPY", child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        while "status" in response:
            try:
                response = self.API.sendchildorder(product_code = "FX_BTC_JPY", child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
        return response

    def limit(self, side, price, size, minute_to_expire=None):
        print("Order: Limit. Side : {}".format(side))
        response = {"status":"internalError in order.py"}
        try:
            response = self.API.sendchildorder(product_code = "FX_BTC_JPY", child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        while "status" in response:
            try:
                response = self.API.sendchildorder(product_code = "FX_BTC_JPY", child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
        return response

    def ifdoco_buy(self, api,rikaku,songiri):
        buy = api.sendparentorder(order_method = "IFDOCO", minute_to_expire = 10000,time_in_force="GTC",
                                 parameters = [
                                     {"product_code":"FX_BTC_JPY", "condition_type":"MARKET","side" : "BUY" ,"size": self.SIZE },

                                     {"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side" : "SELL","price":rikaku,"size": self.SIZE},

                                     {"product_code":"FX_BTC_JPY","condition_type":"STOP", "side" : "SELL","trigger_price":songiri,"size": self.SIZE}
                                 ])

    def ifdoco_sell(self, api,rikaku,songiri):
        sell = api.sendparentorder(order_method = "IFDOCO", minute_to_expire = 10000,time_in_force="GTC",
                                 parameters = [
                                     {"product_code":"FX_BTC_JPY", "condition_type":"MARKET","side" : "SELL" ,"size": self.SIZE },

                                     {"product_code":"FX_BTC_JPY","condition_type":"LIMIT","side" : "BUY","price":rikaku,"size": self.SIZE},

                                     {"product_code":"FX_BTC_JPY","condition_type":"STOP", "side" : "BUY","trigger_price":songiri,"size": self.SIZE}
                                 ])
    def cancelAllorder(self):
       self.API.cancelallchildorders(product_code="FX_BTC_JPY")
