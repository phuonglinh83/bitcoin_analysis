import sys
import re
import datetime
import numpy as np
from os import listdir
from os.path import join
import matplotlib
import matplotlib.pyplot as plt

def load_price(file_path, prices):
    lines = open(file_path, 'r').readlines()
    for line in lines[1:]:
        if not line.strip():
            break
        tokens = line.split(',')
        stringtime = tokens[0].replace('\"', '').strip()
        time = datetime.datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S')
        price = float(tokens[1].strip())
        prices[time] = price

def join_price(hourly_file, prices, fromTime, toTime):
    results = []
    for line in open(hourly_file, 'r'):
        tokens = line.split(',')
        time = datetime.datetime.strptime(tokens[0].replace('\"', '').strip(), '%Y-%m-%d %H:%M:%S')
         # Each data point is a tuple of (time, total, #pos, #neg, price)
        data = (time, int(tokens[1].strip()), int(tokens[2].strip()), int(tokens[3].strip()), prices[time])
        if time >= fromTime and time < toTime:
            # print (str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "," + str(data[4]))
            results.append(data)
    return results
        

if __name__ == "__main__":
    sentiment_report_file = sys.argv[1]
    price_dir = sys.argv[2]
    fromTime = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d')
    toTime = datetime.datetime.strptime(sys.argv[4], '%Y-%m-%d')
    outfile = open(sys.argv[5], 'w')
    
    # a dictionary map each hour to the closing price of that hour
    prices = dict()
    # load prices from all files in a dir into the dictionary for look up
    for filename in listdir(price_dir):
        file_path = join(price_dir, filename)
        load_price(file_path, prices)
    
    # 1. Now report correlation between sentiments and prices for each day
    for day in range(0, (toTime - fromTime).days):
        startTime = fromTime + datetime.timedelta(days=day)
        endTime = fromTime + datetime.timedelta(days=day + 1)
        
        # join sentiment data with prices first
        raw = join_price(sentiment_report_file, prices, startTime, endTime)
        
        # Compute two series (each point in a serie is for an hour)
        # s1 for (pos - neg)/total
        s1 = []
        # s2 for prices
        s2 = []
        for i in range(0, len(raw)):
            diff_sentiment = (0.0 + raw[i][2] - raw[i][3]) / raw[i][1]
            s1.append(diff_sentiment)
            s2.append(raw[i][4])
        print "%d-%d-%d,%f" %(startTime.year, startTime.month, startTime.day, np.corrcoef(s1, s2)[0][1])
    
    # 2. write all results to the outfile
    all_data = join_price(sentiment_report_file, prices, fromTime, toTime)
    for data  in all_data:
        outfile.write(str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "," + str(data[4]) + '\n')
    outfile.close()