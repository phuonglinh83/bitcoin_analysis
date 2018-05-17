# bitcoin_analysis
Analyze twitter sentiment on bitcoin price

1. Setup
Install tweepy:
sudo pip install tweepy
sudo pip install textblob

2. Download tweets about #btc to file tweets.txt
python download_tweet.py a.txt

if hitting 'Rate limit exceed', continue to run the same command in next 15 mins

3. Filter tweets by days

python filter.py a.txt '2018-03-05 00:00:00' '2018-03-05 23:59:59' tweets/3_05.txt

4. Report
- Single file:
python report.py tweets/3_04.txt

- Whole directory
python report.py tweets


