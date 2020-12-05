# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:05:40 2020

This script trains a machine learning classifier to predict whether a tweet was from Donald Trump
or from a parody account. To create the training set, it pulls 1000 tweets from @realDonaldTrump
and 1000 tweets from parody accounts (500 from @realDonaldTrFan and 500 from @RealDonalDrumpf)
Then a logaritmic support vector machine classifier (SGDClassifier with a log loss) is trained
on the data.

@author: Guido Meijer
"""

import tweepy
import time
import pandas as pd
import numpy as np
from datetime import date
from joblib import load
import matplotlib.pyplot as plt
import seaborn as sns

NUM_REAL = 50
NUM_FAKE = 50


def tweepy_to_df(tweets, real, twitter_data=[]):
    if len(twitter_data) == 0:
        twitter_data = pd.DataFrame()

    for i in range(len(tweets)):
        twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = tweets[i].full_text
        twitter_data.loc[twitter_data.shape[0], 'id'] = int(tweets[i].id)
        twitter_data.loc[twitter_data.shape[0], 'date'] = tweets[i].created_at
        twitter_data.loc[twitter_data.shape[0], 'real'] = real
    return twitter_data


# Authenticate to Twitter
api_keys = pd.read_csv('keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# %% Query tweets
print('\nScraping tweets for game..\n')

# Get tweets from Trump
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='realDonaldTrump', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
twitter_data = tweepy_to_df(tweets, 1)
oldest = tweets[-1].id - 1
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='realDonaldTrump', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True, max_id=oldest)
twitter_data = tweepy_to_df(tweets, 1, twitter_data)

# Get tweets from parody accounts
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
twitter_data = tweepy_to_df(tweets, 0, twitter_data)

# Get first block of tweets
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='RealDonalDrumpf', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
twitter_data = tweepy_to_df(tweets, 0, twitter_data)

# %% Build dataframe

# Clean up text
twitter_data['link'] = 0
for i, index in enumerate(twitter_data.index.values):
    # Replace '&' character
    twitter_data.loc[index, 'text'] = twitter_data.loc[index, 'text'].replace('&amp;', '&')

    # Create field excluding the link
    if 'http' in twitter_data.loc[index, 'text']:
        twitter_data.loc[index, 'link'] = 1

# Remove empty entries and entries with link
twitter_data = twitter_data[twitter_data['text'] != '']
twitter_data = twitter_data[twitter_data['link'] == 0]

# %% Play game

# Select random number of real and fake tweets for game
twitter_data = pd.concat([twitter_data[twitter_data['real'] == 1].sample(NUM_REAL, replace=False),
                          twitter_data[twitter_data['real'] == 0].sample(NUM_FAKE, replace=False)])

# Shuffle order
twitter_data = twitter_data.sample(frac=1).reset_index()

# Start game
name = input('What is your name?')
print('Input r for real and p for parody\n')
for i, tweet in enumerate(twitter_data['text']):
    print('Tweet %d of %d\n' % (i + 1, twitter_data.shape[0]))
    print(tweet)
    user_input = input('Real (r) or parody (p)?')
    while (user_input != 'r') and (user_input != 'p'):
        print('Input r or p')
        user_input = input('Real (r) or parody (p)?')
    if (twitter_data.loc[i, 'real'] == 1) & (user_input == 'r'):
        print('\nCorrect!\n')
    elif (twitter_data.loc[i, 'real'] == 0) & (user_input == 'p'):
        print('\nCorrect!\n')
    elif (twitter_data.loc[i, 'real'] == 1) & (user_input == 'p'):
        print('\nWrong answer..\n')
    elif (twitter_data.loc[i, 'real'] == 0) & (user_input == 'r'):
        print('\nWrong answer..\n')
    time.sleep(1)
    twitter_data.loc[i, 'user'] = user_input
    twitter_data.to_csv('user_data_tweets_%s.csv' % name)

# Reformat
twitter_data.loc[twitter_data['user'] == 'r', 'user'] = 1
twitter_data.loc[twitter_data['user'] == 'p', 'user'] = 0

# Add correct
twitter_data['correct'] = twitter_data['real'] + twitter_data['user']
twitter_data.loc[twitter_data['correct'] == 2, 'correct'] = 0
twitter_data['correct'] = 1 - twitter_data['correct']

print('\nYou had %.1f%% correct\n' % (twitter_data['correct'].mean() * 100))
twitter_data.to_csv('user_data_tweets_%s.csv' % name)
