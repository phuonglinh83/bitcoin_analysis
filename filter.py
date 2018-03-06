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

if __name__ == "__main__":
    infile = sys.argv[1]
    fromTime = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d %H:%M:%S')
    toTime = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d %H:%M:%S')
    outfile = sys.argv[4]
    filter(infile, fromTime, toTime, outfile)