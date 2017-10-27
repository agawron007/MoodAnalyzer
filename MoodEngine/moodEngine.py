#!/usr/bin/env python
"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""

import os
import re
import logging
import pandas as pd
import numpy as np
import nltk.data
from bs4 import BeautifulSoup
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

from textProcessingUtils import clean_review

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
    return mood

def SendToPrognosis(mood):
    result = "<Result><Keyword>" + ','.join(keywords) + "</Keyword><Mood>" + str(mood) + "</Mood></Result>"

    base_url="http://10.116.1.82:4000"

    payload = result
    response = requests.post(base_url, data=payload)

    print(response.text) #TEXT/HTML

def pushDataToServer():
  global lastIntervalMoods
  threading.Timer(updateTimeInSec, pushDataToServer).start()
  if len(lastIntervalMoods) == 0:
    SendToPrognosis(lastMood)
    print "No feeds, sending last mood"
    return
  
  moodIndexResult = sum(lastIntervalMoods)* 100 /(len(lastIntervalMoods))
  global lastMood
  lastMood = moodIndexResult[0]
  lastIntervalMoods = []
  print "Feeding Prognosis with mood data from last " + str(updateTimeInSec) + ". Average mood was: " + str(lastMood)
  SendToPrognosis(lastMood)


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
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print post_data
        data = json.loads(post_data)

        receivedText = data["Text"]
        global keywords
        keywords = data["Keywords"]
        print receivedText
        moodValue = calculateMood(receivedText)
        lastIntervalMoods.append(moodValue)
        
def run(server_class=HTTPServer, handler_class=S, port=1234):
    server_address = ('10.116.1.27', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        pushDataToServer()
        run()

