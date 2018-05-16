import re
import sys
import tweepy
import subprocess
from tweepy import OAuthHandler
import os.path
 
class TwitterClient(object):
    # Twitter Client for getting tweets about #btc.
    def __init__(self):
        self.index = 0
        self.set_up_acct()
        
    def set_up_acct(self):
        consumer_key = []
        consumer_secret = []
        access_token = []
        access_token_secret = []
        
        # Set up two accounts, if one hits the rate limit use the other 
        consumer_key.append('Ga8UVgu8frXMA3FLVuAKigXNv')
        consumer_secret.append('3NPsacxonz8n1MAhwdFKVrIK6QqPYm9hKxRpKp5UBxKTWtbGVg')
        access_token.append('201938486-lbGaPchclw2o4n4MRwgVM41dsGWC0cHNhKrI22Y5')
        access_token_secret.append('cDiQWaW4r3tcGxSF0cov67YufrdXwETo5yGPqWkiYSnAy')
        
        consumer_key.append('4N3y0laRvzfTdfuQkHSuhaLUG')
        consumer_secret.append('PPrbaLQi4klmRienvQ0nkd8GIjbMQM5wQKAWfdr7xMYHx5rckP')
        access_token.append('970396032927334400-R0HtHb1NTvGnNM01QY5qWyr3sl7UnMH')
        access_token_secret.append('swjEjepUxIBojF089QVS3tTL8srYFGrdvXB5fnHtFWJYm')
 
        # attempt the first authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key[self.index], consumer_secret[self.index])
            # set access token and secret
            self.auth.set_access_token(access_token[self.index], access_token_secret[self.index])
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
 
    # Does initial tweet cleaning text by removing account links, special characters
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])(\w+:\/\/\S+)", " ", tweet).split())
 
    # Simple API call to get the latest tweet id of tweets about a query
    def get_latest_tweet(self, query):
        fetched_tweets = tweepy.Cursor(self.api.search, q=query, rpp=5).items(5)
        
    # Main func to fetch 'count' tweets about a 'query' up to 'max_id'.
    # Fetched tweets are order by tweet ids (time)
    def get_tweets(self, query, count, max_id):
        # list to store the result
        tweets = []    
        while len(tweets) < count:
            try:
                # call twitter search api to fetch tweets
                fetched_tweets = self.api.search(q = query, max_id=max_id, count = 100)
              
                # process downloaded tweets one by one
                for tweet in fetched_tweets:
                    print tweet.id_str + "|"  + str(tweet.created_at)
                    
                    # Only keep tweets in English
                    if tweet.id_str == max_id or tweet.metadata['iso_language_code'] != 'en':
                        # Update max_id for the next api call
                        max_id = tweet.id_str
                        continue
                    
                    # Dictionary to store required params of a tweet
                    parsed_tweet = {}
     
                    # saving text of tweet
                    parsed_tweet['text'] = tweet.text
                    # saving id of tweet
                    parsed_tweet['id'] = tweet.id_str
                    # saving created time of tweet
                    parsed_tweet['time'] = str(tweet.created_at)
     
                    # appending parsed tweet to tweets list
                    tweets.append(parsed_tweet)
                    
                    # Update max_id for the next api call
                    max_id = tweet.id_str
 
                print "Saving %d tweets" %(len(tweets))
 
            except tweepy.TweepError as e:
                print("Error : " + str(e))
                # Switching to the other account
                self.index = (self.index + 1) % 2
                self.set_up_acct()
        return tweets
 
# Appends downloaded tweets into a file
def writeTweets(tweets, outfile):
  outfile = open(outfile, 'a')
  for tweet in tweets:
    # Change encoding of tweet text, remove '|' and '\n' character before writing to file
    txt = tweet['text'].encode('utf-8').decode('ascii', 'ignore').replace('|', '').replace('\n', ' ')
    # Line format <tweet_id>|<time>|<text>
    line = tweet['id'] + '|' + tweet['time'] + '|' + txt
    outfile.write(line + '\n')
  outfile.close()
  return

# Get the last id of downloaded tweets from a file.
# If file does not exist, call twitter api to get the lastest id
def getLastId(api, query, outfile):
    if os.path.isfile(outfile):
      # File exists, run os 'tail' command to get last lines
      lines = subprocess.check_output(['tail', outfile]).strip().split('\n')
      
      # Get latest id from the last line
      tokens = lines[-1].split('|')
      return tokens[0]
    
    # Otherwise call twitter api
    return api.get_latest_tweet(query)

# Keep this script running until get killed to get more tweets in the past  
if __name__ == "__main__":
    # File to store downloaded tweets. If not exist, we will create a new one
    # Raw tweets in this file are sorted in decreasing time order
    resultFile = sys.argv[1]
    
    # creating object of TwitterClient Class
    api = TwitterClient()
    
    # bitcoin query
    query = '#btc'
    
    # We keep this loop running to get more tweets in the past.
    while True:
      # First get the last tweet id of tweets about bitcoin from the previous result.
      max_id = getLastId(api, query, resultFile)
      
      # Then download tweets older than max_id
      tweets = api.get_tweets(query = query, count = 100, max_id = max_id)
      
      # Finally append downloaded into result file
      writeTweets(tweets, resultFile)
 
 