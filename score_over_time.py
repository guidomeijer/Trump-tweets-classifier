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
import seaborn as sns


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
real_tweets = tweepy_to_df(tweets)

# Query more until date is reached
while real_tweets.loc[real_tweets.shape[0], 'date'].date() > date(2020, 1, 1):
    print('Scraped %d tweets from realDonaldTrump..' % real_tweets.shape[0])
    new_tweets = []
    while len(new_tweets) == 0:
        new_tweets = api.user_timeline(screen_name='realDonaldTrump', count=200,
                                       include_rts=False, tweet_mode='extended',
                                       exclude_replies=True, max_id=oldest)
    oldest = new_tweets[-1].id - 1
    real_tweets = tweepy_to_df(new_tweets, real_tweets)

# %% Query tweets from realDonaldTrFan

# Get first block of tweets
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
oldest = tweets[-1].id - 1
fake_tweets1 = tweepy_to_df(tweets)

# Query more until date is reached
while fake_tweets1.loc[fake_tweets1.shape[0], 'date'].date() > date(2020, 1, 1):
    print('Scraped %d tweets from realDonaldTrFan..' % fake_tweets1.shape[0])
    new_tweets = []
    while len(new_tweets) == 0:
        new_tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200,
                                       include_rts=False, tweet_mode='extended',
                                       exclude_replies=True, max_id=oldest)
    oldest = new_tweets[-1].id - 1
    fake_tweets1 = tweepy_to_df(new_tweets, fake_tweets1)

# %% Query tweets from RealDonalDrumpf

# Get first block of tweets
tweets = []
while len(tweets) == 0:
    tweets = api.user_timeline(screen_name='RealDonalDrumpf', count=200, include_rts=False,
                               tweet_mode='extended', exclude_replies=True)
oldest = tweets[-1].id - 1
fake_tweets2 = tweepy_to_df(tweets)

# Query more until date is reached
while fake_tweets1.loc[fake_tweets2.shape[0], 'date'].date() > date(2020, 1, 1):
    print('Scraped %d tweets from RealDonalDrumpf..' % fake_tweets2.shape[0])
    new_tweets = []
    while len(new_tweets) == 0:
        new_tweets = api.user_timeline(screen_name='RealDonalDrumpf', count=200,
                                       include_rts=False, tweet_mode='extended',
                                       exclude_replies=True, max_id=oldest)
    oldest = new_tweets[-1].id - 1
    fake_tweets2 = tweepy_to_df(new_tweets, fake_tweets2)

# %% Build dataframe

real_tweets['real'] = 1
fake_tweets1['real'] = 0
fake_tweets2['real'] = 0
twitter_data = pd.concat([real_tweets, fake_tweets1, fake_tweets2])

# Clean up text
for i, index in enumerate(twitter_data.index.values):
    # Replace '&' character
    twitter_data.loc[index, 'text'] = twitter_data.loc[index, 'text'].replace('&amp;', '&')

    # Create field excluding the link
    no_link = list(filter(lambda x: 'http' not in x, twitter_data.loc[index, 'text'].split()))
    tweet_without_link = ' '.join(word for word in no_link)
    twitter_data.loc[index, 'text_no_link'] = tweet_without_link

# Remove empty entries
twitter_data = twitter_data[twitter_data['text_no_link'] != '']

# Save this dataset
twitter_data.to_csv('%s_all_tweets_since_january.csv' % str(date.today()))

"""
# Load in the fully trained linear support vector machine classifier
clf = load('2020-05-14_SGD_model.joblib')

# Classify all tweets
twitter_data = twitter_data.reset_index()
for i, tweet_text in enumerate(twitter_data['text_no_link']):

    # Get probability that its from the parody account
    prediction = clf.predict([tweet_text])[0]
    probability = clf.predict_proba([tweet_text])[0][0]

    # Add to the dataframe
    twitter_data.loc[i, 'probability'] = probability

# Plot results
f, ax1 = plt.subplots(1, 1, figsize=(5, 5))
sns.scatterplot(x='date', y='probability', data=twitter_data, ax=ax1)
ax1.set(xlim=[date(2020, 4, 1), date(2020, 7, 1)])

"""