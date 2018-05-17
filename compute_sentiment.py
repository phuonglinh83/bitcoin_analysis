import sys
import datetime
from os import listdir
from os.path import isfile, isdir, join
from textblob import TextBlob
from clean_filter import clean_tweet, filter_tweet

# Use TextBlob to classify sentiment of a tweet
def get_tweet_sentiment(tweet):
    # create TextBlob object of passed tweet text
    analysis = TextBlob(tweet)

    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

# Reports sentiment results by hour. In each hour we report
# - Total number of tweets
# - Total number of positive tweets
# - Total number of nevative tweets
def report(filename, results):
    # List of all tweets in each hour to remove duplications
    all_tweets = []
    hour = -1
    # Counters
    neg = 0
    pos = 0
    total = 0
    prev_time = ''
    for line in open(filename, 'r'):
        tokens = line.split('|')
        time = datetime.datetime.strptime(tokens[1], '%Y-%m-%d %H:%M:%S')
        # Round up time to hour
        roundTime = datetime.datetime(time.year, time.month, time.day, time.hour)  
        if hour < roundTime.hour:
            if hour >= 0:
                # Report results for the hour
                results.append((prev_time, total, pos, neg))
            # Reset counters for a new hour
            hour = roundTime.hour
            neg = 0
            pos = 0
            total = 0
            all_tweets = []
        
        # First clean tweet
        cleaned = clean_tweet(tokens[2])
        if filter_tweet(cleaned) and cleaned not in all_tweets:
            # The filters (a lot of retweets are removed here)
            all_tweets.append(cleaned)
            # Compute the sentiment
            sentiment = get_tweet_sentiment(cleaned)
            if sentiment == 'positive':
                pos = pos + 1
            elif sentiment == 'negative':
                neg = neg + 1
            total = total + 1
        prev_time = roundTime
    
    # Report results for the final hour
    results.append((prev_time, total, pos, neg))
    return 

if __name__ == "__main__":
    path = sys.argv[1]
    outfile = open(sys.argv[2], 'w')
    results = []
    if isfile(path):
        # If input is a file, process this file only
        report(path, results)
    elif isdir(path):
        # If input is a dir, process all files in that dir
        paths = listdir(path)
        paths.sort()
        for filename in paths:
            file_path = join(path, filename)
            if isfile(file_path):
                report(file_path, results)
    
    results.sort(key = lambda x : x[0])
    for tup in results:
        outfile.write("%d-%d-%d %d:00:00, %d, %d, %d"%(tup[0].year, tup[0].month, tup[0].day, tup[0].hour, tup[1] , tup[2], tup[3]) + '\n')
    outfile.close()