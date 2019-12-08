#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import time
import matplotlib.pyplot as plt


with open('board_3.csv', 'r') as f:
    reader = csv.reader(f)

    order_list = []
    yakujo_list = []
    order = 0
    for data in reader:
        best_ask, best_bid, buy_size, sell_size = 0, 0, 0, 0
        for d in data:
            d = d.strip("[")
            d = d.strip("]")
            i = d.split(", ")
            if i[1] == "'BUY'":
                best_ask = int(i[0])
                buy_size += float(i[2])
            elif i[1] == "'SELL'":
                best_bid = int(i[0])
                sell_size += float(i[2])
        if best_ask == 0:
            best_ask = best_bid+50
        elif best_bid == 0:
            best_bid = best_ask-50

        for o in order_list[:]:
            if o[2] > 10:
                order_list.remove(o)
                continue
            elif o[1] == "BUY" and o[0] > best_bid and order <= 3:
                yakujo_list.append(o)
                order_list.remove(o)
                order += 1
            elif o[1] == "SELL" and o[0] < best_ask and order >= -3:
                yakujo_list.append(o)
                order_list.remove(o)
                order += -1
            o[2] += 1
        if order <= 3 and order >= -3:
            order_list.append([best_bid-300, "BUY", 0])
            order_list.append([best_ask+300, "SELL", 0])
        elif order >= 3:
            order_list.append([best_ask+300, "SELL", 0])
        elif order <= -3:
            order_list.append([best_bid-300, "BUY", 0])
    amount = 0
    order = 0
    max_order = 0
    min_order = 0
    sui = []
    yakujo = []
    print(len(yakujo_list))
    for y in yakujo_list:
        if y[1] == "BUY":
            amount -= y[0]*0.01
            order += 1
            yakujo.append(amount)
        elif y[1] == "SELL":
            amount += y[0]*0.01
            order += -1
            yakujo.append(amount)
        if max_order < order:
            max_order = order
        if min_order > order:
            min_order = order
        if order == 0:
            sui.append(amount)
    if order != 0:
        amount += order*yakujo_list[-1][0]*0.01
        yakujo.append(amount)
    print(max_order)
    print(min_order)
    print(amount)
    # print(yakujo)
    # print(sui)
    plt.plot(sui)
    plt.show()
