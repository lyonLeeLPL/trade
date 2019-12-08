#_*_ coding: utf-8 _*_
import csv
number = 1
while True:
    file_name1 = "executions_" + str(number)
    with open('{}.csv'.format(file_name1), 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        execution = reversed(list(reader))
        yakujo = []
        side = ''
        for line in execution:
            time = line[4][17] + line[4][18]
            price = round(float(line[2]))
            yakujo.append([[price, time, line[4]]])
            break
        for line in execution:
            price = round(float(line[2]))
            time = line[4][17] + line[4][18]
            if yakujo[-1][-1][1] == time:
                yakujo[-1].append([price, time, line[4]])
            else:
                yakujo.append([[price, time, line[4]]])
        li = []
        for i in yakujo:
            high = i[0][0]
            low = i[0][0]
            close = i[-1][0]
            time = i[-1][2]
            for k in i:
                if high < k[0]:
                    high = k[0]
                elif low > k[0]:
                    low = k[0]
            li.append([high, low, close, time])

    file_name2 = "board_" + str(number)
    with open('{}.csv'.format(file_name2), 'a') as g:
        writer = csv.writer(g, lineterminator='\n') # 改行コード（\n）を指定しておく
        for i in li:
            writer.writerow(i)
    number += 1
