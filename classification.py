import sys
import nltk
import random
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer

pos1 = ['time bonus still active purchases buy spark coinspark',
        'remember downtrend market tonight hold coins best performance buy others tomorro',
        'keep calm amp buy xrpthestandard hold xrp ripple bitcoin erium optimistic hodl trx bch ada',
        'bought buzzshow tokens presale dont worry still chance buy toke',
        'days left join eroiy_coin pre buy tokens bonus waiting grab',
        'bitcoin fingers crossed gather enough buying volume continuously trade upwards',
        'serious downtrend maybe low bitcoin go buythedip',
        'top rising cryptocurrencies last minutes',
        'iota looks interesting long term buy price bounced fib leveland chart suggest accumulation befor',
        'great opportunity buy pure start masternode project developing exchange atomic swaps pure holders',
        'invest future future digibyte used buy goods services quickly keep',
        'buying skyrocketing right per minute crypto cryptocurrency',
        'bullish pennant possible target k bitcoin btfd tothemoon ta log lambo litecoin crypto',
        'recent cryptocurrency dive means market buy cryptocurrency cryptonews',
        'good news todayexcept nucleous vision listed binance bitcoin bitcoinnews crypto cryptofan',
        'donnycrypto please everyone dont miss train time',
        'next target million need make huge money huge profit contact privet join grou',
        'cryptochoe moon soon success bitcoin alts well dont miss golden opp',
        'ill honest get followers make happy crypto cryptocurrency litecoin ereum',
        'time pump looking bullish history repeats']

neg1 = ['bubble popped another pumpanddump dont buy wings expect price dip sats',
        'anyone else feel last giant dip january selling bitcoin',
        'cryptocurrencies crypto cryptocurrency sure require courage hold sell',
        'taiwan sees first bitcoin robbery lesson dont sell bitcoin crime get apps',
        'nano huge deep hours actual top crypto currency price index nano bitcoin',
        'anyone participating pump dump shitcoin circus ups h crypto',
        'update pay stop loss triggered position closed loss sys currently',
        'stormy today cryptomarket decreased actual cap b top market cap b',
        'populous huge deep hours actual top crypto currency price index ucash bitcoin',
        'realistically speaking tomorow p main net launches p price probably drop first da',
        'whole stock market going aex dow stocks holding strong hodling gems',
        'bitcoin crushing wall st nearly month straight sampp index wallstyousuck',
        'ereum classic biggest loser past week sentiments turn bullish ambcrypto',
        'man arrested selling bitcoin gov alleges received known proceeds illegal activity defendant claim',
        'risky sell anything heavy weight hitter usd litecoin',
        'scam thats old markets talking asset selling dumb money pours se',
        'watched massive k sell wall vanish instantly usd',
        'bad day entire portfolio red cryptocurrency blockchain req neo coss ven trx xrp xlm',
        'found text exchange wan na cry punch self bitcoin',
        'chatcoin closing april sorry bad news bitcoin chatcoin openchat openchatcoin xvg verge']

# Global variables to store all positive tweets
postweets = []
# Global variables to store all negative tweets
negtweets = []
# Global variables to store all words in feature vectors
word_features = []

vectorizer = TfidfVectorizer();

# Builds the feature vector for a tweet
def get_features(tweet):
    words = set(tweet)
    # feature is a dict from a word in word_features to either True or False.
    # True if the word is in the tweet and false otherwise
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

def get_feat2(feats):
    res = {}
    for i in range(0, len(feats)):
        res[i] = feats[i]
    return res;

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
    # print all_words.most_common(20)
    
    # Then pick the top 2000 most common words for building feature vector
    word_features = list(all_words.keys())[:500]
    
    # Shuffle tweets to create randomness
    random.shuffle(postweets)
    random.shuffle(negtweets)
    
    vectorizer.fit(word_features)
    # print(vectorizer.vocabulary_)
    # print(vectorizer.idf_[:10])
    
def get_feature_vec(tweets, label):
    feats = vectorizer.transform(tweets).todense().tolist();
    return [(get_feat2(feat), label) for feat in feats]

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

def textblob_acc(pos_tweets, neg_tweets):
    tb_pos = textblob_correct_rate(pos_tweets, True)
    tb_neg = textblob_correct_rate(neg_tweets, False)
    return (0.0 + tb_pos[0] + tb_neg[0]) / (tb_pos[1] + tb_neg[1])

def cross_validation(training):
    random.shuffle(training)
    num_folds = 5
    subset_size = len(training)/num_folds
    nb_accuracy = 0
    me_accuracy = 0
    me_algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[0]
    for i in range(num_folds):
        testing_this_round = training[i*subset_size:][:subset_size]
        training_this_round = training[:i*subset_size] + training[(i+1)*subset_size:]
        bayes = NaiveBayesClassifier.train(training_this_round)
        nb_accuracy += nltk.classify.util.accuracy(bayes, testing_this_round)
        maxent = nltk.MaxentClassifier.train(training_this_round, me_algorithm, max_iter=1)
        me_accuracy += nltk.classify.util.accuracy(maxent, testing_this_round)

    return (nb_accuracy / 5, me_accuracy / 5)

if __name__ == "__main__":
    fileName = sys.argv[1]
    # Loads training data from input file
    load_data(fileName)
    
    # Then build feature vectors for both negative and positive tweets
    negfeats = get_feature_vec(negtweets, 'neg')
    posfeats = get_feature_vec(postweets, 'pos')

    all_feats = negfeats + posfeats 
    random.shuffle(all_feats)
    
    print 'TextBlog accuracy on training data:', textblob_acc(postweets, negtweets);
    result = cross_validation(all_feats)
    print 'Naiave Bayes cross validation accuracy:', result[0]
    print 'MaxEnt cross validation accuracy:', result[1]

    pos1feats = get_feature_vec(pos1, 'pos')
    neg1feats = get_feature_vec(neg1, 'neg')
    
    all1_feats = neg1feats + pos1feats 

    print 'TextBlog accuracy on manual dataset:', textblob_acc(pos1, neg1);
    bayes = NaiveBayesClassifier.train(all_feats)
    print 'Naiave Bayes accuracy on manual dataset:', nltk.classify.util.accuracy(bayes, all1_feats)
    maxent = nltk.MaxentClassifier.train(all_feats, nltk.classify.MaxentClassifier.ALGORITHMS[0], max_iter=1)
    print 'MaxEnt accuracy on manual dataset:', nltk.classify.util.accuracy(maxent, all1_feats)
    