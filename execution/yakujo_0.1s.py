#_*_ coding: utf-8 _*_
import csv
number = 0
while True:
    file_name1 = "executions_" + str(number)
    with open('{}.csv'.format(file_name1), 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        execution = reversed(list(reader))
        yakujo = []
        side = ''
        size = 0
        for line in execution:
            time = line[4][20]
            price = round(float(line[2]))
            side = line[1]
            size = float(line[3])
            yakujo.append([[price, side, size, time, line[4]]])
            break
        for line in execution:
            price = round(float(line[2]))
            if len(line[4]) < 20:
                time = yakujo[-1][-1][3]
            else:
                time = line[4][20]
            side = line[1]
            size = float(line[3])
            if yakujo[-1][-1][3] == time or time == str(int(yakujo[-1][-1][3])+1)[-1]:
                yakujo[-1].append([price, side, size, time, line[4]])
            else:
                yakujo.append([[price, side, size, time, line[4]]])
        # li = []
        # for i in yakujo:
        #     high = i[0][0]
        #     low = i[0][0]
        #     close = i[-1][0]
        #     time = i[-1][2]
        #     for k in i:
        #         if high < k[0]:
        #             high = k[0]
        #         elif low > k[0]:
        #             low = k[0]
        #     li.append([high, low, close, time])

    file_name2 = "board1_" + str(number)
    with open('{}.csv'.format(file_name2), 'a', newline='') as g:
        writer = csv.writer(g) # 改行コード（\n）を指定しておく
        writer.writerows(yakujo)
    number += 1
