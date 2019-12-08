import csv
import time
import matplotlib.pyplot as plt
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

def eval_backtest(individual):
    price1 = individual[0]
    price2 = individual[1]
    size = individual[2]
    # backtest(bid_price1,bid_price2,ask_price1,ask_price2,size):
    with open('board_4.csv', 'r') as f:
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
            if buy_size - sell_size >= 0 and buy_size - sell_size < size and order <= 3 :
                order_list.append([best_bid-price1, "BUY", 0])
            elif buy_size - sell_size >= size and order <= 3:
                order_list.append([best_bid-price2, "BUY", 0])
            elif sell_size - buy_size >= 0 and sell_size - buy_size < size and order >= -3:
                order_list.append([best_ask+price1, "SELL", 0])
            elif sell_size - buy_size >= size and order >= -3:
                order_list.append([best_ask+price2, "SELL", 0])
        amount = 0
        order = 0
        max_order = 0
        min_order = 0
        sui = []
        yakujo = []
        # print(len(yakujo_list))
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
        # print(max_order)
        # print(min_order)
        # print(amount)
        # print(yakujo)
        # print(sui)
        # plt.plot(sui)
        # plt.show()
        return amount,

import random
from deap import base
from deap import creator
from deap import tools
# backtest(bid_price1,bid_price2,ask_price1,ask_price2,size):
price1 = 10
price2 = 50
size = 1
list_price1 = []
list_price2 = []
list_size = []


while price1 <= 300:
   list_price1.append(price1)
   price1 += 5
while price2 <= 1000:
   list_price2.append(price2)
   price2 += 10
while size <= 20:
   list_size.append(size)
   size += 1

def shuffle(container):
   params = [list_price1,list_price2,list_size]
   shuffled = []
   for x in params:
       shuffled.append(random.choice(x))
   return container(shuffled)

def mutShuffle(individual, indpb):
  params = [list_price1,list_price2,list_size]
  for i in range(len(individual)):
      if random.random() < indpb:
          individual[i] = random.choice(params[i])
  return individual,

#適合度クラスを作成
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

#個体生成関数,世代生成関数を定義
toolbox.register("individual", shuffle, creator.Individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#評価関数,交叉関数,突然変異関数,選択関数を定義
toolbox.register("evaluate", eval_backtest)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutShuffle, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():

   #個体をランダムにn個生成し、初期世代を生成
   pop = toolbox.population(n=10) #n:世代の個体数
   CXPB, MUTPB, NGEN = 0.5, 0.2, 40 #交叉確率、突然変異確率、ループ回数

   print("Start of evolution")

   #初期世代の全個体の適応度を目的関数により評価
   fitnesses = list(map(toolbox.evaluate, pop))
   for ind, fit in zip(pop, fitnesses):
       ind.fitness.values = fit

   print("  Evaluated %i individuals" % len(pop))

   #ループ開始
   for g in range(NGEN):
       print("-- Generation %i --" % g)

       #現行世代から個体を選択し次世代に追加
       offspring = toolbox.select(pop, len(pop))
       offspring = list(map(toolbox.clone, offspring))

       #選択した個体に交叉を適応
       for child1, child2 in zip(offspring[::2], offspring[1::2]):
           if random.random() < CXPB:
               toolbox.mate(child1, child2)
               del child1.fitness.values
               del child2.fitness.values

       #選択した個体に突然変異を適応
       for mutant in offspring:
           if random.random() < MUTPB:
               toolbox.mutate(mutant)
               del mutant.fitness.values

       #適応度が計算されていない個体を集めて適応度を計算
       invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
       fitnesses = map(toolbox.evaluate, invalid_ind)
       for ind, fit in zip(invalid_ind, fitnesses):
           ind.fitness.values = fit

       print("  Evaluated %i individuals" % len(invalid_ind))

       #次世代を現行世代にコピー
       pop[:] = offspring

       #全個体の適応度をlistに格納
       fits = [ind.fitness.values[0] for ind in pop]

       #適応度の最大値、最小値、平均値、標準偏差を計算
       length = len(pop)
       mean = sum(fits) / length
       sum2 = sum(x*x for x in fits)
       std = abs(sum2 / length - mean**2)**0.5

       print("  Min %s" % min(fits))
       print("  Max %s" % max(fits))
       print("  Avg %s" % mean)
       print("  Std %s" % std)
       best_ind = tools.selBest(pop, 1)[0]
       print("Best parameter is %s, %s" % (best_ind, best_ind.fitness.values))

   print("-- End of (successful) evolution --")

   #最後の世代の中で最も適応度の高い個体のもつパラメータを準最適解として出力
   best_ind = tools.selBest(pop, 1)[0]
   print("Best parameter is %s, %s" % (best_ind, best_ind.fitness.values))

if __name__ == "__main__":
   main()
