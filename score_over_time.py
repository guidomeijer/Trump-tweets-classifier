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
from datetime import date
from joblib import load
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import seaborn as sns
import numpy as np


def tweepy_to_df(tweets, twitter_data=[]):
    if len(twitter_data) == 0:
        twitter_data = pd.DataFrame()

    for i in range(len(tweets)):
        twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = tweets[i].full_text
        twitter_data.loc[twitter_data.shape[0], 'date'] = tweets[i].created_at
    return twitter_data


# Authenticate to Twitter
api_keys = pd.read_csv('keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# %% Query tweets from real Donald Trump

# Get first block of tweets
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='realDonaldTrump', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
oldest = tweets[-1].id - 1
twitter_data = tweepy_to_df(tweets)

# Query more until amount is reached
while twitter_data.shape[0] <= 1800:
    print('Scraped %d tweets from realDonaldTrump..' % twitter_data.shape[0])
    new_tweets = []
    while len(new_tweets) == 0:
        new_tweets = api.user_timeline(screen_name='realDonaldTrump', count=200,
                                       include_rts=False, tweet_mode='extended',
                                       exclude_replies=True, max_id=oldest)
    oldest = new_tweets[-1].id - 1
    twitter_data = tweepy_to_df(new_tweets, twitter_data)
print('Done')

# %% Build dataframe

# Clean up text
for i, index in enumerate(twitter_data.index.values):
    # Replace '&' character
    twitter_data.loc[index, 'text'] = twitter_data.loc[index, 'text'].replace('&amp;', '&')

# Remove empty entries
twitter_data = twitter_data[twitter_data['text_no_link'] != '']

# Remove entries with links
twitter_data = twitter_data[twitter_data['text'].str.find('http') == -1]

# Load in the fully trained linear support vector machine classifier
clf = load('2020-05-14_SGD_model.joblib')

# Classify all tweets
twitter_data = twitter_data.reset_index()
for i, tweet_text in enumerate(twitter_data['text']):

    # Get probability that its from the parody account
    prediction = clf.predict([tweet_text])[0]
    probability = clf.predict_proba([tweet_text])[0][0]

    # Add to the dataframe
    twitter_data.loc[i, 'probability'] = probability

# %% Plot

# Get data to plot
plot_data = twitter_data[twitter_data['probability'] > 0.5]

# Calculate convolved rolling-avereage score over time
#score_conv = np.convolve(plot_data['probability'].rolling(window=7).mean(),
#                         np.ones((3,))/3, mode='valid')
#score_conv = np.append(score_conv, [np.nan, np.nan])
score_conv = medfilt(plot_data['probability'].rolling(window=10).mean(), kernel_size=3)

f, ax1 = plt.subplots(1, 1, figsize=(10, 10), dpi=150)
ax1.scatter(plot_data['date'], plot_data['probability'])
ax1.plot(plot_data['date'], score_conv)

