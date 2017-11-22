#!/usr/bin/env python

import sys
sys.path.insert(0,'../Common')
sys.path.insert(0,'../PriceCollector')

import os
import re
import csv
import logging
import pandas as pd
import numpy as np
import nltk.data
from bs4 import BeautifulSoup
from datetime import datetime
from nltk.corpus import stopwords
from gensim.models import word2vec
from sklearn import naive_bayes, svm, preprocessing
from sklearn.decomposition import TruncatedSVD
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection.univariate_selection import chi2, SelectKBest

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import threading
import pickle
import json

import sentiment_mod as s

from app_price_collector import PriceCollector
from textProcessingUtils import clean_review
from textblob_sentiment_engine import TextBlobSentimentEngine

from mood_logger import Logger

updateTimeInSec = 30.0

lastIntervalMoods = []

#load model

# Getting back the objects:

with open('model.pickle') as f:  # Python 3: open(..., 'rb')
    nb = pickle.load(f)

with open('count_vec.pickle') as f:  # Python 3: open(..., 'rb')
    count_vec = pickle.load(f)

with open('fselect.pickle') as f:  # Python 3: open(..., 'rb')
    fselect = pickle.load(f)

keywords = ""
lastMood = 0

import requests

def calculateMood(myReview):
    global nb
    testList = []
    testVec = []
    testList.append(clean_review(myReview))
    print testList
    testVec = count_vec.transform(testList)
    print testVec
    testVec = fselect.transform(testVec)
    print '\n'
    print testVec
    print '\n'
    mood = nb.predict(testVec)
    print 'Prediction: ' + str(mood)
    return mood * 1.0, 1.0

def calculateMood2(text):
    mood = TextBlobSentimentEngine.calculate(text)
    Logger.log_debug("Sentiment >> " + str(mood) + ' << for text: ' + text)
    return mood, 1.0

def calculateMood3(text):
    mood, confidence = s.sentiment(text)
    Logger.log_debug("Sentiment >> " + str(mood) + ' << for text: ' + text)
    mood = 1.0 if mood == 'pos' else 0.0
    return mood, confidence * 1.0


class MoodPublisher:
    def __init__(self):
        self.price_collector = PriceCollector()

    def SendToServer(self, mood):
        with open('mood.csv', 'a') as csvfile:
            currentTime = str(datetime.now())
            posts_writer = csv.writer(csvfile, delimiter='\t',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            current_price = self.price_collector.get_current_price()
            posts_writer.writerow([currentTime, mood, current_price, ','.join(keywords)])

            Logger.log_debug('!!!VVVVVVVVVVVVVVVVVVVVVVVVVVV!!!')
            Logger.log_debug(','.join(map(str,[currentTime, mood, current_price, ','.join(keywords)])))
            Logger.log_debug('!!!^^^^^^^^^^^^^^^^^^^^^^^^^^^!!!')
    def pushDataToServer(self):
        global lastIntervalMoods
        threading.Timer(updateTimeInSec, self.pushDataToServer).start()
        if len(lastIntervalMoods) == 0:
            Logger.log_debug("Waiting for first feeds")
            return

        while len(lastIntervalMoods) > 1000:
            lastIntervalMoods.pop(0)
        Logger.log_debug("Num of elements: " + str(len(lastIntervalMoods)))
        moodIndexResult = sum(lastIntervalMoods)* 100 /(len(lastIntervalMoods))
        global lastMood
        lastMood = int(moodIndexResult)
        self.SendToServer(lastMood)

class S(BaseHTTPRequestHandler):
    

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        Logger.log_debug("Received POST request with length: " + str(content_length))
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        data = json.loads(post_data)

        receivedText = data["Text"]
        global keywords
        keywords = data["Keywords"]
        textSource = data["Source"]
        currentTime = str(datetime.now())
        self.writeTextToFile(currentTime, textSource, receivedText)

        #moodValue = calculateMood(receivedText)
        moodValue, confidence = calculateMood3(receivedText)
        Logger.log_debug("calculated sentiment: " + str(moodValue) + " with confidence: " + str(confidence))
        if (confidence > 0.8):
            lastIntervalMoods.append(moodValue)

    def writeTextToFile(self, currentTime, textSource, text):
        with open('data.csv', 'a') as csvfile:
            posts_writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            posts_writer.writerow([currentTime, textSource, text])

def run(server_class=HTTPServer, handler_class=S, port=1234):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    Logger.log_debug('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    mood_publisher = MoodPublisher()

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        mood_publisher.pushDataToServer()
        run()

