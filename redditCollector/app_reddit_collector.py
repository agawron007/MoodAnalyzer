
import sys
sys.path.insert(0,'../Common')

import requests
import json
import time
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import unicodedata
import datetime

import re
from restful_publisher import http_post_record
from reddit_api_token import get_reddit_api
from mood_logger import Logger

import praw

subredditName = "bitcoin"

def get_date(submission):
    time = submission.created
    return datetime.datetime.fromtimestamp(time)

def start_streaming(subreddit):
    for comment in subreddit.stream.comments():
        comment.body = unicodedata.normalize('NFKD', comment.body).encode('ascii','ignore')
        Logger.log_debug(str(get_date(comment)) + '|' + str(comment.submission) + '|' + comment.body)
        http_post_record(comment.body, subredditName)

def main():
    while True:
        try:
            reddit = get_reddit_api()
            subreddit = reddit.subreddit(subredditName)
            start_streaming(subreddit)
        except:
            e = sys.exc_info()[0]
            Logger.log_error("Reddit streaming crashed. Retrying. Exception: " + str(e))
            continue

main()

'''
subreddit_comments = subreddit.comments(limit=100)
#subreddit_comments.replace_more(limit=0)

commentsPerSubmission = {"id": "comment"}
commentsPerSubmission.clear()

for comment in subreddit_comments:
    comment.body = unicodedata.normalize('NFKD', comment.body).encode('ascii','ignore')
    print comment.body
    print comment.submission
    print get_date(comment)
    key = comment.fullname
    #if commentsPerSubmission.has_key(key):
    #    commentsPerSubmission[key].append(comment.body)
    #else:
    commentsPerSubmission[key] = [comment.body]
    
print(commentsPerSubmission)'''
'''
for submission in subreddit.hot(limit=2):
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print(submission.title)  # Output: the submission's title
    print(submission.score)  # Output: the submission's score
    print(submission.id)     # Output: the submission's ID
    print(submission.url)    # Output: the URL the submission points to
                             # or the submission's URL if it's a self post
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        text = comment.body
        text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
        print(text)

submission = reddit.submission(url='https://www.reddit.com/r/funny/comments/3g1jfi/buttons/')


submission.comments.replace_more(limit=0)
for comment in submission.comments.list():
    text = comment.body
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
    #print(text)
    '''