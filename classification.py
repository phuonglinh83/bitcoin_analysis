import sys
import nltk
import random
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from textblob import TextBlob

# Global variables to store all positive tweets
postweets = []
# Global variables to store all negative tweets
negtweets = []
# Global variables to store all words in feature vectors
word_features = []

# Builds the feature vector for a tweet
def get_features(tweet):
    words = set(tweet)
    # feature is a dict from a word in word_features to either True or False.
    # True if the word is in the tweet and false otherwise
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

# Loads training data from file
def load_data(filename):
    # store words in all tweets
    all_words = []
    for line in open(filename, 'r'):
        tokens = line.split('|')
        if tokens[0] == 'positive':
            postweets.append(tokens[1])
        else:
            negtweets.append(tokens[1])
        
        # Collect all words in the tweets
        for word in tokens[1].split(' '):
            all_words.append(word.strip())
    
    # Build frequency distribution for all words
    all_words = nltk.FreqDist(all_words)
    print all_words.most_common(20)
    
    # Then pick the top 2000 most common words for building feature vector
    word_features = list(all_words.keys())[:2000]
    
    # Shuffle tweets to create randomness
    random.shuffle(postweets)
    random.shuffle(negtweets)


def textblob_correct_rate(tweets, is_pos):
    correct = 0
    total = 0
    for tweet in tweets:
        analysis = TextBlob(tweet)
        # For fair comparison, we remove tweets that TextBlob classifies as neutral (with popularity = 0)
        if (is_pos and analysis.sentiment.polarity > 0) or (not is_pos and analysis.sentiment.polarity < 0):
            # TextBlob prediction matches training data
            correct = correct + 1
        if analysis.sentiment.polarity != 0:
            total = total + 1
    return (correct, total)


if __name__ == "__main__":
    fileName = sys.argv[1]
    # Loads training data from input file
    load_data(fileName)
    
    # Then build feature vectors for both negative and positive tweets
    negfeats = [(get_features(tweet), 'neg') for tweet in negtweets]
    posfeats = [(get_features(tweet), 'pos') for tweet in postweets]
    
    # Use 75% for training, 25% for testing
    negcutoff = len(negfeats)*3/4
    poscutoff = len(posfeats)*3/4
 
    # training set: 75% instances
    trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
    # testing set: 25% instances
    testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
    print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
    
    # Compute the accuracy for TextBlob
    tb_pos = textblob_correct_rate(postweets[poscutoff:], True)
    tb_neg = textblob_correct_rate(negtweets[negcutoff:], False)
    textblob_acc = (0.0 + tb_pos[0] + tb_neg[0]) / (tb_pos[1] + tb_neg[1])
    print 'TextBlog accuracy:', textblob_acc
 
    # Apply Naive Bayes classifier from nltk 
    classifier = NaiveBayesClassifier.train(trainfeats)
    print 'Naiave Bayes accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
    
    # Apply MaxEnt classifier from nltk 
    algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[0]
    classifier = nltk.MaxentClassifier.train(trainfeats, algorithm,max_iter=3)  
    print 'MaxEnt accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
    
    