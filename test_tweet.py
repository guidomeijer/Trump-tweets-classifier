# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:05:40 2020

@author: Guido
"""

import tweepy
import pandas as pd
from datetime import date
from os.path import join
from joblib import load

# Authenticate to Twitter
api_keys = pd.read_csv('D:\Repositories\Trump-tweets-classifier\keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth)

# Create test tweet
tweet_text = 'I AM THE BEST PRESIDENT EVER'
tweet_real = 0

# Load in the fully trained linear support vector machine classifier
clf = load('2020-05-13_SGD_model.joblib')

# Classify tweet
prediction = clf.predict([tweet_text])[0]
probability = clf.predict_proba([tweet_text])[0]

# Tweet results
first_tweet = api.update_status(tweet_text)
if prediction == 0:
	second_tweet = api.update_status(
        ('I predict this tweet is FAKE with a probability of %d%%, what do you think?'
         % (probability[0] * 100)),
        in_reply_to_status_id=first_tweet.id)
elif prediction == 1:
	second_tweet = api.update_status(
        ('I predict this tweet is REAL with a probability of %d%%, what do you think?'
         % (probability[1] * 100)),
        in_reply_to_status_id=first_tweet.id)
if (prediction == 0) & (tweet_real == 0):
	third_tweet = api.update_status('I was right, this tweet was FAKE',
                                 in_reply_to_status_id=second_tweet.id)
elif (prediction == 1) & (tweet_real == 0):
	third_tweet = api.update_status('I was wrong, this tweet was FAKE',
                                 in_reply_to_status_id=second_tweet.id)
elif (prediction == 1) & (tweet_real == 1):
	third_tweet = api.update_status('I was right, this tweet was REAL',
                                 in_reply_to_status_id=second_tweet.id)
elif (prediction == 0) & (tweet_real == 1):
	third_tweet = api.update_status('I was wrong, this tweet was REAL',
                                 in_reply_to_status_id=second_tweet.id)
