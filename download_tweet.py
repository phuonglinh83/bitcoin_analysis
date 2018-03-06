import re
import sys
import tweepy
import subprocess
from tweepy import OAuthHandler
from textblob import TextBlob
import os.path
 
class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        self.index = 0
        self.set_up_acct()
        
    def set_up_acct(self):
        consumer_key = []
        consumer_secret = []
        access_token = []
        access_token_secret = []
        
        consumer_key.append('Ga8UVgu8frXMA3FLVuAKigXNv')
        consumer_secret.append('3NPsacxonz8n1MAhwdFKVrIK6QqPYm9hKxRpKp5UBxKTWtbGVg')
        access_token.append('201938486-lbGaPchclw2o4n4MRwgVM41dsGWC0cHNhKrI22Y5')
        access_token_secret.append('cDiQWaW4r3tcGxSF0cov67YufrdXwETo5yGPqWkiYSnAy')
        
        consumer_key.append('4N3y0laRvzfTdfuQkHSuhaLUG')
        consumer_secret.append('PPrbaLQi4klmRienvQ0nkd8GIjbMQM5wQKAWfdr7xMYHx5rckP')
        access_token.append('970396032927334400-R0HtHb1NTvGnNM01QY5qWyr3sl7UnMH')
        access_token_secret.append('swjEjepUxIBojF089QVS3tTL8srYFGrdvXB5fnHtFWJYm')
 
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key[self.index], consumer_secret[self.index])
            # set access token and secret
            self.auth.set_access_token(access_token[self.index], access_token_secret[self.index])
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
 
    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])(\w+:\/\/\S+)", " ", tweet).split())
 
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # print analysis.sentiment
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
 
    def get_latest_tweet(self, query):
        fetched_tweets = tweepy.Cursor(self.api.search, q=query, rpp=5).items(5)
        for tweet in fetched_tweets:
            print tweet.id_str + ":"  + str(tweet.created_at)
            return tweet.id_str
        
    def get_tweets(self, query, count, max_id):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
        
        while len(tweets) < count :
            try:
                # call twitter api to fetch tweets
                fetched_tweets = self.api.search(q = query, max_id=max_id, count = 100)
                # fetched_tweets = self.api.search(q = query, count = count, until = 'Fri Sep 21 23:40:54 +0000 2012')
                # fetched_tweets = tweepy.Cursor(self.api.search, q=query, max_id=max_id).items(100)
                # fetched_tweets = tweepy.Cursor(self.api.search, q=query, rpp=10, lang='en', max_id=max_id).items(count)
     
                # parsing tweets one by one
                for tweet in fetched_tweets:
                    # print tweet.metadata
                    # break
                    print tweet.id_str + "|"  + str(tweet.created_at)
                    if tweet.id_str == max_id or tweet.metadata['iso_language_code'] != 'en':
                        max_id = tweet.id_str
                        continue
                    
                    # print tweet.id_str + "|"  + str(tweet.created_at)
                    # empty dictionary to store required params of a tweet
                    parsed_tweet = {}
     
                    # saving text of tweet
                    parsed_tweet['text'] = tweet.text
                    # saving sentiment of tweet
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                    parsed_tweet['id'] = tweet.id_str
                    parsed_tweet['time'] = str(tweet.created_at)
     
                    # appending parsed tweet to tweets list
                    if tweet.retweet_count > 0:
                        # if tweet has retweets, ensure that it is appended only once
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)
                    max_id = tweet.id_str
 
                print "Filtered tweets: %d "%(len(tweets))
            # return parsed tweets
            # return tweets
 
            except tweepy.TweepError as e:
                # print error (if any)
                print("Error : " + str(e))
                self.index = (self.index + 1) % 2
                self.set_up_acct()
        return tweets
 
def writeTweets(tweets, outfile):
  #write output to file for apriori input
  outfile = open(outfile, 'a')
  for tweet in tweets:
    txt = tweet['text'].encode('utf-8').decode('ascii', 'ignore').replace('|', '').replace('\n', ' ')
    line = tweet['sentiment'] + '|' + tweet['id'] + '|' + tweet['time'] + '|' + txt
    outfile.write(line + '\n')
  outfile.close()
  return

def getLastId(api, query, outfile):
    if os.path.isfile(outfile) :
        lines = subprocess.check_output(['tail', outfile]).strip().split('\n')
        tokens = lines[-1].split('|')
        return tokens[1]
    return api.get_latest_tweet(query)
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    resultFile = sys.argv[1]
    query = '#btc'
    # calling function to get tweets
    while True:
        max_id = getLastId(api, query, resultFile)
        print max_id
        tweets = api.get_tweets(query = query, count = 100, max_id = max_id)
        if len(tweets) == 0:
            break
        writeTweets(tweets, resultFile)
 
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    
    print "Total tweets: %d, pos %d, neg %d "%(len(tweets), len(ptweets), len(ntweets))
    # percentage of positive tweets
    # print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    
    # percentage of negative tweets
    # print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    # print("Neutral tweets percentage: {} %".format(100*len(tweets - ntweets - ptweets)/len(tweets)))
 
    # printing first 5 positive tweets
    # print("\n\nPositive tweets:")
    # for tweet in ptweets[:1]:
    #     print(tweet['text'])
 
    # printing first 5 negative tweets
    # print("\n\nNegative tweets:")
    # for tweet in ntweets[:1]:
    #     print(tweet['text'])
 
if __name__ == "__main__":
    # calling main function
    main()