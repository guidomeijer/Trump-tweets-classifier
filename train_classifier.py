# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:05:40 2020

@author: Guido
"""

import tweepy
import pandas as pd
from datetime import date
from os.path import join
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Authenticate to Twitter
api_keys = pd.read_csv('D:\Repositories\Trump-tweets-classifier\keys.csv')
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
while len(real_tweets) < 1000:
    new_real_tweets = api.user_timeline(screen_name='realDonaldTrump', count=200,
                                        include_rts=False, tweet_mode='extended',
                                        exclude_replies=True, max_id=oldest)
    real_tweets.extend(new_real_tweets)
    oldest = real_tweets[-1].id - 1

# Save to dataframe
for i in range(len(real_tweets)):
    twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = real_tweets[i].full_text
    twitter_data.loc[twitter_data.shape[0], 'real'] = 1

# Query tweets from parody account
fake_tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200, include_rts=False,
                                tweet_mode='extended', exclude_replies=True)
oldest = fake_tweets[-1].id - 1
while len(fake_tweets) < 1000:
    new_fake_tweets = api.user_timeline(screen_name='realDonaldTrFan', count=200,
                                        include_rts=False, tweet_mode='extended',
                                        exclude_replies=True, max_id=oldest)
    fake_tweets.extend(new_fake_tweets)
    oldest = fake_tweets[-1].id - 1

# Add to dataframe
for i in range(len(fake_tweets)):
    twitter_data.loc[twitter_data.shape[0] + 1, 'text'] = fake_tweets[i].full_text
    twitter_data.loc[twitter_data.shape[0], 'real'] = 0

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
twitter_data.to_csv(join('data', '%s_twitter_training_data.csv' % str(date.today())))

# Initialize linear support vector machine classifier (SGDClassifier)
pipeline_sgd = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('nb', SGDClassifier(loss='log'))])

# Train on half of the dataset and predict the other half to get a sense of performance
X_train, X_test, y_train, y_test = train_test_split(twitter_data['text_no_link'],
                                                    twitter_data['real'],
                                                    random_state=42)
cross_val_model = pipeline_sgd.fit(X_train, y_train)
y_predict = cross_val_model.predict(X_test)
print(classification_report(y_test, y_predict))

# Now train on the full dataset
full_model = pipeline_sgd.fit(twitter_data['text_no_link'].values, twitter_data['real'].values)
dump(full_model, '%s_SGD_model.joblib' % str(date.today()))
