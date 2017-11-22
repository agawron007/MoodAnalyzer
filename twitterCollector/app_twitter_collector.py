
import sys
sys.dont_write_bytecode = True
sys.path.insert(0,'../Common')
sys.path.insert(0,'../Tokens')

from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json
import nltk
import unicodedata
from mood_logger import Logger

from twitter_key_token import get_auth
from restful_publisher import http_post_record
from text_utils import remove_new_lines
from text_utils import normalize

import time

keywords = ['bitcoin']
class MyListener((tweepy.StreamListener)):
    def on_status(self, data):
        data.text = normalize(data.text)
        data.text = remove_new_lines(data.text)
        try:
            #all_data = json.loads(data)
            tweet = data.text
            Logger.log_debug(tweet)
            http_post_record(tweet, ','.join(keywords), "twitter")
            #sentiment_value, confidence = nltk.sentiment(tweet)
            #print(tweet, sentiment_value, confidence)

            '''if confidence*100 >= 80:
                # creates the file.
                # fills it in with data
                output = open('twitterAnalyzed.txt','a')
                output.write(sentiment_value)
                #separates
                output.write('\n')
                output.close()'''
            return True

        except:
            e = sys.exc_info()[0]
            Logger.log_error("Failed process tweet. Exception: " + str(e))
            return True

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False



def start_stream():
    while True:
        try:
            auth = get_auth()
            listener = MyListener()
            twitterStream = Stream(auth, listener)
            twitterStream.filter(track=keywords, stall_warnings=True)
        except: 
            e = sys.exc_info()[0]
            Logger.log_error("Reddit streaming crashed. Retrying. Exception: " + str(e))
            continue

start_stream()