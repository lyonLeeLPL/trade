#_*_ coding: utf-8 _*_
import csv

with open('executions_0.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    execution = reversed(list(reader))
    list = []
    side = ''
    for line in execution:
        side = line[1]
        best_ask = round(float(line[2]))
        best_bid = round(float(line[2]))
        size = round(float(line[3]), 2)
        time = line[4]
        break
    list.append([best_ask, best_bid, size, side, time])
    print(list)
    for line in execution:
        if line[1] == 'BUY':
            best_ask = round(float(line[2]))
        elif line[1] == 'SELL':
            best_bid = round(float(line[2]))
        side = line[1]
        size = round(float(line[3]), 2)
        time = line[4]
        if list[-1][4] == time:
            size += list[-1][2]
            list.pop()
        list.append([best_ask, best_bid, size, side, time])

with open('board_0.csv', 'a') as g:
    writer = csv.writer(g, lineterminator='\n') # 改行コード（\n）を指定しておく
    for i in list:
        writer.writerow(i)
