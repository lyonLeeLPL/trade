#!/usr/bin/env python3
#_*_ coding: utf-8 _*_
# Time-stamp: <2018-05-19 16:39:31>
#---------------------------------------------------------------------------------------------
import sys
import csv
import datetime
import argparse

##設定値
#元データのCSVファイル名　元データのCSVファイルは「https://api.bitcoincharts.com/v1/csv/」で取得できます
input_file_name = "data.csv"
#作成する4本値のCSVファイル名
output_file_name = "data_out.csv"
#集計を開始する日付＋時刻
kijyun_date = datetime.datetime.strptime('20170704 17:15:00', '%Y%m%d %H:%M:%S')
#分足の単位。例えば5分足なら「minutes=5」
kizami_date = datetime.timedelta(minutes=5)
# kizami_date = datetime.timedelta(minutes=3)
# kizami_date = datetime.timedelta(minutes=1)

# build up command line argment parser
parser = argparse.ArgumentParser(
            usage='OHLCV data Converter',
            description='description',
            epilog='',
            add_help=True, )
parser.add_argument('-i', '--infile',  help='input csv data file')
parser.add_argument('-o', '--outfile', help='output csv data file')
parser.add_argument('-t', '--interval', help='OHLCV interval(60, 180, 300)',type=int)

# 引数を解析する
args = parser.parse_args()
if args.infile:
    input_file_name = args.infile
if args.outfile:
    output_file_name = args.outfile
if args.interval:
    kizami_date = args.interval

#CSV読み込み
csv_file = open(input_file_name, "r", encoding="ms932", errors="", newline="" )
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="", quotechar='"', skipinitialspace=True)

#4本値を計算
datalist = []
priceH = 0
priceT = 0
priceY = 0
priceO = 0
for row in f:
    if (datetime.datetime.fromtimestamp(int(row[0])) < kijyun_date + kizami_date):
        if priceH == 0:
            priceH = int(row[1].replace('.000000000000',''))
            priceT = int(row[1].replace('.000000000000',''))
            priceY = int(row[1].replace('.000000000000',''))
            priceO = int(row[1].replace('.000000000000',''))
        else:
            if priceT < int(row[1].replace('.000000000000','')):
                priceT = int(row[1].replace('.000000000000',''))
            if priceY > int(row[1].replace('.000000000000','')):
                priceY = int(row[1].replace('.000000000000',''))
    else:
        if priceH > 0:
            priceO = int(row[1].replace('.000000000000',''))
        datalist_new = int(row[0]), priceH, priceT, priceY, priceO, 0
        if priceH == 0 and priceT == 0 and priceY == 0 and priceO == 0:
            print("SKIP blank")
        else:
            datalist.append(datalist_new)
        kijyun_date = kijyun_date + kizami_date
        priceH = 0
        priceT = 0
        priceY = 0
        priceO = 0

#CSVファイルに出力する
csv_file = open(output_file_name, 'w', encoding='UTF-8')
csv_writer = csv.writer(csv_file, lineterminator='\n')
for j in range(len(datalist)):
    csv_writer.writerow(datalist[j])
csv_file.close()
print("convert done.")
