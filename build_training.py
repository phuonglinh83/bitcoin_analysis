import sys
import re
from os import listdir
from os.path import isfile, isdir, join
from clean_filter import clean_tweet, filter_tweet
       
def is_positive(tweet, algorithm):
    if algorithm == 'price-move':
        if re.search(r'\+\d*.\d*%', tweet):
            return True
        return False
    
    if algorithm == 'emoticon':
        if ':)' in tweet or ':-)' in tweet or ':D' in tweet:
            return True
        return False
    
    if algorithm == 'buy-sell':
        lowertweet = tweet.lower()
        if 'buy' in lowertweet:
            return True
        return False
    
    if algorithm == 'all':
        lowertweet = tweet.lower()
        if re.search(r'\+\d*.\d*%', tweet) or ':)' in tweet or ':-)' in tweet or ':D' in tweet or 'buy' in lowertweet:
            return True
        return False
    
    raise ValueError('Invalid training algorithm!')

def is_negative(tweet, algorithm):
    if algorithm == 'price-move':
        if re.search(r'\-\d*.\d*%', tweet):
            return True
        return False
    
    if algorithm == 'emoticon':
        if ':(' in tweet or ':-(' in tweet:
            return True
        return False
    
    if algorithm == 'buy-sell':
        lowertweet = tweet.lower()
        if 'sell' in lowertweet:
            return True
        return False
    
    if algorithm == 'all':
        lowertweet = tweet.lower()
        if re.search(r'\-\d*.\d*%', tweet) or ':(' in tweet or ':-(' in tweet or 'sell' in lowertweet:
            return True
        return False
    
    raise ValueError('Invalid training algorithm!')

def process(filename, algorithm, outfile):
    all_tweets = []
    for line in open(filename, 'r'):
        tokens = line.split('|')
        origin = tokens[2]
        label = ''
        
        is_pos = is_positive(origin, algorithm)
        is_neg = is_negative(origin, algorithm)
        
        if is_pos and not is_neg:
            # positive only
            label = 'positive'
        elif is_neg and not is_pos:
            # negative only
            label = 'negative'

        if label != '':
            # if tweet has a label, clean and write to output file
            cleaned = clean_tweet(origin)
            if filter_tweet(cleaned) and cleaned not in all_tweets:
                all_tweets.append(cleaned)
                outfile.write(label + "|" + cleaned + '\n')
                # outfile.write(cleaned)

if __name__ == "__main__":
    path = sys.argv[1]
    algorithm = sys.argv[2]
    outfile = open(sys.argv[3], 'w')
    
    if isfile(path):
        # If input is a file, process this file only
        process(path, algorithm, outfile)
    elif isdir(path):
        # If input is a dir, process all files in that dir
        paths = listdir(path)
        # Sort files by name
        paths.sort()
        for filename in paths:
            file_path = join(path, filename)
            if isfile(file_path):
                process(file_path, algorithm, outfile)
    outfile.close()
