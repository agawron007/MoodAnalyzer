# import tweepy library for twitter api access and textblob libary for sentiment analysis
import csv
import tweepy
import sys
import numpy as np
import datetime as dt
import time
from textblob import TextBlob
from twitter_key_token import load_api
import re
from restful_api import http_post_record

max_tweets = 100                           # number of tweets per search (will be
                                               # iterated over) - maximum is 100
USA = '39.8,-95.583068847656,2500km'       # this geocode includes nearly all American
                                               # states (and a large portion of Canada)

def main():

    # set path of csv file to save sentiment stats
    path = 'mood.csv'

    twitter_api = load_api()

    # fetch tweets by keywords
    q=['bitcoin, price']
    last_id = get_tweet_id(twitter_api, days_ago=(1))
    while True:
        try:
            tweets, last_id = tweet_search(twitter_api, q, max_tweets, since_id=last_id, geocode=USA)
            tweets = clean_tweets(tweets)

            for tweet in tweets:
                http_post_record(tweet.text, q[0])

            # generate sentiment stats
            get_sentiment_stats(tweets, get_polarity, get_subjectivity)

            # save sentiment data to csv file
            save_sentiment_to_csv(tweets, path, classify_sentiment)
            time.sleep(60)

        except KeyboardInterrupt:
            print "\nBye\n"
            sys.exit()
        #except:
        #    e = sys.exc_info()[0]
        #    print "Runtime error, trying again. " + str(e)
    #twitter_api.search(q=['bitcoin, price'], lang='en', count=100)

    

def get_tweet_id(api, date='', days_ago=9, query='a'):
    ''' Function that gets the ID of a tweet. This ID can then be
        used as a 'starting point' from which to search. The query is
        required and has been set to a commonly used word by default.
        The variable 'days_ago' has been initialized to the maximum
        amount we are able to search back in time (9).'''

    if date:
        # return an ID from the start of the given day
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search(q=query, lang='en', count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        # get list of up to 10 tweets
        tweet = api.search(q=query, lang='en', count=10, until=tweet_date)
        print('search limit (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0].id

def tweet_search(api, query, max_tweets, since_id, geocode):
    ''' Function that takes in a search string 'query', the maximum
        number of tweets 'max_tweets', and the minimum (i.e., starting)
        tweet id. It returns a list of tweepy.models.Status objects. '''
    last_id = since_id
    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, lang='en', count=remaining_tweets,
                                    since_id=str(last_id))
#                                    geocode=geocode)
            print('found',len(new_tweets),'tweets')
            if not new_tweets:
                print('no tweets found')
                break
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
            
        except tweepy.TweepError:
            print('exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, last_id

def clean_tweets(tweets):
    clean_tweets_array = []
    for tweet in tweets:
        tweet.text = clean_tweet(tweet.text)
        clean_tweets_array.append(tweet)
    return clean_tweets_array

def clean_tweet(content):
    p = re.compile(ur'[\r?\n]')
    content = re.sub(p, r' ', content)
    content = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',content)
    content = re.sub('[^0-9a-zA-Z\s,\.]+', '', content)
    return content

def get_polarity(tweets):
    # run polarity analysis on tweets

    tweet_polarity = []

    for tweet in tweets:
        analysis = TextBlob(tweet.text)
        tweet_polarity.append(analysis.sentiment.polarity)

    return tweet_polarity


def get_subjectivity(tweets):
    # run subjectivity analysis on tweets

    tweet_subjectivity = []

    for tweet in tweets:
        analysis = TextBlob(tweet.text)
        tweet_subjectivity.append(analysis.sentiment.subjectivity)

    return tweet_subjectivity


def classify_sentiment(analysis, threshold = 0):
    # classify sentiment polarity as positive or negative

    if analysis.sentiment.polarity > threshold:
        return 'Positive'
    elif analysis.sentiment.polarity < threshold:
        return 'Negative'
    else:
        return 'Neutral'


def get_sentiment_stats(tweets, get_polarity, get_subjectivity):
    # generate sentiment stats

    polarity = get_polarity(tweets)
    subjectivity = get_subjectivity(tweets)

    print('Polarity count: %s' % np.count_nonzero(polarity))
    print('Polarity average: %.3f' % np.mean(polarity))
    print('Polarity standard deviation: %.3f' % np.std(polarity))
    print('Polarity coefficient of variation: %.3f' % (np.std(polarity) / np.mean(polarity)))
    print('********')
    print('Subjectivity count: %s' % np.count_nonzero(subjectivity))
    print('Subjectivity average: %.3f' % np.mean(subjectivity))
    print('Subjectivity standard deviation: %.3f' % np.std(subjectivity))
    print('Subjectivity coefficient of variation: %.3f' % (np.std(subjectivity) / np.mean(subjectivity)))


def save_sentiment_to_csv(tweets, path, classify_sentiment):
    # save tweets, polarity, subjectivity, and sentiment class to csv file
    with open(path, 'a') as f:
        writer = csv.writer(f)
        f.write('tweet, polarity, subjectivity, sentiment_class\n')

        for tweet in tweets:
            analysis = TextBlob(tweet.text)
            print "created at: " + str(tweet.created_at)
            writer.writerow([str(dt.datetime.now()), str(tweet.created_at), tweet.text.encode('utf8'), analysis.sentiment.polarity, analysis.sentiment.subjectivity, classify_sentiment(analysis)])

        f.close()


if __name__ == '__main__':
    main()