import sys
import re
import datetime

def filter(infile, fromTime, toTime, outfile):
    outfile = open(outfile, 'w')
    lines = []
    for line in open(infile, 'r'):
        tokens = line.split('|')
        # print tokens
        time = datetime.datetime.strptime(tokens[2], '%Y-%m-%d %H:%M:%S')
        if time >= fromTime and time < toTime:
            lines.append(line)
    for line in lines[::-1]:
        outfile.write(line)
    outfile.close()

# Filter raw downloaded tweets into days, one file per day. These files are saved in tweets_by_day dir
# Tweets in each file are sorted in increasing time order.
# Call python filter.py <raw_tweets_file> <month> <from_day> <to_day> 
if __name__ == "__main__":
    infile = sys.argv[1]
    month = int(sys.argv[2])
    fromday = int(sys.argv[3])
    today = int(sys.argv[4])
    for day in range(fromday, today + 1):
        fromTime = datetime.datetime(2018, month, day, 0, 0, 0)
        toTime = datetime.datetime(2018, month, day, 23, 59, 59)
        # print fromTime
        # print toTime
        outfile = 'tweets_by_day/' + str(month) + '_' + str(day) + '.txt'
        # print outfile
        filter(infile, fromTime, toTime, outfile)