# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:05:40 2020

@author: Guido Meijer
"""

import tweepy
import pandas as pd
from joblib import load

# Authenticate to Twitter
api_keys = pd.read_csv('D:\\Repositories\\Trump-tweets-classifier\\keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth)

# Create test tweet
tweet_text = 'OBAMAGATE!'
tweet_real = 1

# Load in the fully trained linear support vector machine classifier
clf = load('2020-05-14_SGD_model.joblib')

# Classify tweet
prediction = clf.predict([tweet_text])[0]
probability = clf.predict_proba([tweet_text])[0]
probability = probability[int(prediction)]

# Tweet results
# Post original tweet
try:
    first_tweet = api.update_status(tweet_text)
except:
    print('Tweet was already tweeted, abort!')

# Post prediction of the classifier
if (prediction == 0) & (tweet_real == 0):
    api.update_status(
        ('I predict this tweet is FAKE with a probability of %d%%.\nI was right, this tweet is FAKE.'
         % (probability * 100)), in_reply_to_status_id=first_tweet.id)
elif (prediction == 1) & (tweet_real == 0):
    api.update_status(
        ('Fake news!\nI predict this tweet is REAL (%d%% probability) but it is actually FAKE.'
         % (probability * 100)), in_reply_to_status_id=first_tweet.id)
elif (prediction == 1) & (tweet_real == 1):
    api.update_status(
        ('I predict this tweet is REAL with a probability of %d%%.\nI was right, this tweet is REAL.'
         % (probability * 100)), in_reply_to_status_id=first_tweet.id)
elif (prediction == 0) & (tweet_real == 1):
    api.update_status(
        ('This is weird!\nThis tweet looks FAKE to me (%d%% probability) but it is actually REAL!'
         % (probability * 100)), in_reply_to_status_id=first_tweet.id)
