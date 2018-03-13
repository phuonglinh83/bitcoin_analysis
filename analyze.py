import sys
import re
import datetime
from os import listdir
from os.path import join

def load_price(file_path, prices):
    lines = open(file_path, 'r').readlines()
    for line in lines[1:]:
        if not line.strip():
            break
        tokens = line.split(',')
        stringtime = tokens[0].replace('\"', '').strip()
        # print stringtime
        time = datetime.datetime.strptime(stringtime, '%Y-%m-%d %H:%M:%S')
        price = float(tokens[1].strip())
        prices[time] = price
        # print stringtime + ": %f"%(price)

def join_price(hourly_file, prices):
    results = []
    for line in open(hourly_file, 'r'):
        tokens = line.split(',')
        time = datetime.datetime.strptime(tokens[0].replace('\"', '').strip(), '%Y-%m-%d %H:%M:%S')
        data = (time, int(tokens[1].strip()), int(tokens[2].strip()), prices[time])
        print data
        results.append(data)
    return results
        

if __name__ == "__main__":
    path = 'coindesk'
    prices = dict()
    for filename in listdir(path):
        file_path = join(path, filename)
        # print file_path
        load_price(file_path, prices)
    join_price('hourly.txt', prices)