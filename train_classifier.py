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
import pandas as pd
from datetime import date
from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Authenticate to Twitter
api_keys = pd.read_csv('~/Repositories/Trump-tweets-classifier/keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth)

# Query tweets from real Donald Trump
twitter_data = pd.DataFrame()
real_tweets = api.user_timeline(screen_name='realDonaldTrump', count=200, include_rts=False,
                                tweet_mode='extended', exclude_replies=True)
oldest = real_tweets[-1].id - 1
while len(real_tweets) < 1500:
    new_real_tweets = api.user_timeline(screen_name='realDonaldTrump', count=200,
                                        include_rts=False, tweet_mode='extended',
                                        exclude_replies=True, max_id=oldest)
    real_tweets.extend(new_real_tweets)
    oldest = real_tweets[-1].id - 1

# Save to dataframe
for i in range(len(real_tweets)):
    twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = real_tweets[i].full_text
    twitter_data.loc[twitter_data.shape[0], 'real'] = 1

# Query tweets from parody accounts
fake1_tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200, include_rts=False,
                                 tweet_mode='extended', exclude_replies=True)
oldest = fake1_tweets[-1].id - 1
while len(fake1_tweets) < 750:
    new_fake1_tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200,
                                         include_rts=False, tweet_mode='extended',
                                         exclude_replies=True, max_id=oldest)
    fake1_tweets.extend(new_fake1_tweets)
    oldest = fake1_tweets[-1].id - 1

# Save to dataframe
for i in range(len(fake1_tweets)):
    twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = fake1_tweets[i].full_text
    twitter_data.loc[twitter_data.shape[0], 'real'] = 0

# Other parody account
fake2_tweets = api.user_timeline(screen_name='RealDonalDrumpf', count=200, include_rts=False,
                                 tweet_mode='extended', exclude_replies=True)
oldest = fake2_tweets[-1].id - 1
while len(fake2_tweets) < 750:
    new_fake2_tweets = api.user_timeline(screen_name='RealDonalDrumpf', count=200,
                                         include_rts=False, tweet_mode='extended',
                                         exclude_replies=True, max_id=oldest)
    fake2_tweets.extend(new_fake2_tweets)
    oldest = fake2_tweets[-1].id - 1

# Add to dataframe
for i in range(len(fake2_tweets)):
    twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = fake2_tweets[i].full_text
    twitter_data.loc[twitter_data.shape[0], 'real'] = 0

# Clean up text
for i, index in enumerate(twitter_data.index.values):
    # Replace '&' character
    twitter_data.loc[index, 'text'] = twitter_data.loc[index, 'text'].replace('&amp;', '&')

# Remove empty entries
twitter_data = twitter_data[twitter_data['text'] != '']

# Remove entries with links
twitter_data = twitter_data[twitter_data['text'].str.find('http') == -1]

# Save this dataset
twitter_data.to_csv('%s_twitter_training_data.csv' % str(date.today()))

# Initialize logaritmic support vector machine classifier (SGDClassifier)
pipeline_sgd = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('nb', SGDClassifier(loss='log'))])

# Train on half of the dataset and predict the other half to get a sense of performance
X_train, X_test, y_train, y_test = train_test_split(twitter_data['text'],
                                                    twitter_data['real'],
                                                    random_state=42)
cross_val_model = pipeline_sgd.fit(X_train, y_train)
y_predict = cross_val_model.predict(X_test)
print(classification_report(y_test, y_predict))

# Now train on the full dataset
full_model = pipeline_sgd.fit(twitter_data['text'].values, twitter_data['real'].values)
dump(full_model, '%s_SGD_model.joblib' % str(date.today()))
