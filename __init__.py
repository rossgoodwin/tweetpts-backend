from flask import Flask
from flask.ext.cors import CORS
import tweepy
import json
import re
from collections import Counter
import do_auth

APP_PATH = '/var/www/TweetPts/TweetPts/'

app = Flask(__name__)
cors = CORS(app)

CONSUMER_KEY = do_auth.c_k
CONSUMER_SECRET = do_auth.c_s
ACCESS_TOKEN = do_auth.a_k
ACCESS_TOKEN_SECRET = do_auth.a_s

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

stopwordsFile = open(APP_PATH+'stopwords.txt', 'r')
stopwords = filter(lambda x: x, map(lambda y: y.strip(), stopwordsFile.read().split('\n')))
stopwordsFile.close()

@app.route("/")
def hello():
    # File should look like:
    # HillaryClinton,D
    # DonaldTrump,R
    # ...

    snFile = open(APP_PATH+'sn_list.txt')
    snText = snFile.read()
    snFile.close()

    screennames_parties = sorted(filter(lambda x: x, snText.split('\n')))
    screennames, parties = zip(*map(lambda x: tuple(x.split(',')), screennames_parties))

    # 2D list
    recent_tweets = map(get_recent_tweets, screennames)

    word_freqs = map(word_freq, recent_tweets)

    objs = map(lambda i: {
        'party': parties[i], 
        'words': word_freqs[i],
        'name': screennames[i]
    }, range(len(screennames)))

    return json.dumps(objs)


def get_recent_tweets(screen_name):
    # make request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=25)
    return [tweet.text.encode("utf-8") for tweet in new_tweets]


def word_freq(tweets):
    tweet_str = ' '.join(tweets).lower()
    new_str = ' '.join(filter(lambda x: not x.startswith('http'), tweet_str.split()))
    tokens = filter(lambda x: not x in stopwords, re.findall(r"\b[\w']+\b", new_str))
    return Counter(tokens).most_common()

if __name__ == "__main__":
    app.run()
