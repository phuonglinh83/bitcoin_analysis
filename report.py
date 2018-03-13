import sys
import re
import datetime
from os import listdir
from os.path import isfile, isdir, join

def printResult(day, hour, pos, neg):
    time = datetime.datetime(day.year, day.month, day.day, hour) + datetime.timedelta(hours = 1)
    print "%d-%d-%d %d:00:00, %d, %d"%(time.year, time.month, time.day, time.hour, pos , neg)

def report(filename):
    tweets = []
    hour = -1
    neg = 0
    pos = 0
    total = 0
    time = ''
    for line in open(filename, 'r'):
        tokens = line.split('|')
        time = datetime.datetime.strptime(tokens[2], '%Y-%m-%d %H:%M:%S')
        if hour < time.hour:
            if hour >= 0:
                printResult(time, hour, pos * 100/total, neg*100/total)
            hour = time.hour
            neg = 0
            pos = 0
            total = 0
        if tokens[0] == 'positive':
            pos = pos + 1;
        elif tokens[0] == 'negative':
            neg = neg + 1
        total = total + 1
    printResult(time, hour, pos * 100/total, neg*100/total)
    return 

if __name__ == "__main__":
    path = sys.argv[1]
    if isfile(path):
        report(path)
    elif isdir(path):
        for filename in listdir(path):
            file_path = join(path, filename)
            if isfile(file_path):
                report(file_path)