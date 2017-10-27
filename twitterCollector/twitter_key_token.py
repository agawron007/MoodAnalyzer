import tweepy
from tweepy import OAuthHandler 
    

def load_api():
    ''' Function that loads the twitter API : MoodAnalyzer1026 '''
    # get from twitter develper.. need register yourself
    # consumer_key = 'JGXM2YsNKCzSSpKN1p2WNQTvh'
    # consumer_secret = 'IwvOixkNBLxeJxpsmuwSlgBzGyARsSlQIsk3BqHO8weof66p9E'
    # access_token_key = "285393638-1viTxV1aULuEsvt83nJlJ9d8pnXgrgZ4ib809qwr"
    # access_token_secret = "nUc6yiEuWYGQHzGAFHwQV76fgeaKzp9XsGC8KekkRWfWU"
    
    consumer_key = 'JGXM2YsNKCzSSpKN1p2WNQTvh'
    consumer_secret = 'IwvOixkNBLxeJxpsmuwSlgBzGyARsSlQIsk3BqHO8weof66p9E'
    access_token_key = "285393638-1viTxV1aULuEsvt83nJlJ9d8pnXgrgZ4ib809qwr"
    access_token_secret = "nUc6yiEuWYGQHzGAFHwQV76fgeaKzp9XsGC8KekkRWfWU"

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)
