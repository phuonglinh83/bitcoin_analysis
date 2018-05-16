import nltk
import re

stop_words = set(nltk.corpus.stopwords.words('english'))

# Cleans a tweet
def clean_tweet(tweet):
    # remove http links
    tweet = re.sub(r"(http|https)://\S+", "", tweet)
    # remove punctuation
    tweet = re.sub(r'[^\w\s]','', tweet)
    # remove numbers
    tweet = re.sub(r'\d+','', tweet)
    # to lower case
    tweet = tweet.lower()
    # remove coin symbol
    tweet = re.sub(r"(btc|eth|ltc|ico)","", tweet)
    
    # now remove stopwords
    word_tokens = nltk.tokenize.word_tokenize(tweet)
    filtered = [w for w in word_tokens if not w in stop_words]
    clean_tweet = ""
    for w in filtered:
        clean_tweet = clean_tweet + w + " "
    return clean_tweet.strip()

def filter_tweet(tweet):
    # Eliminate retweets
    if tweet.startswith('rt '):
        return False
    tokens = tweet.split(' ')
    # Eliminate short tweets
    if len(tokens) < 5:
        return False
    return True