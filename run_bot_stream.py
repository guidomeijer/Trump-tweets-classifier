# -*- coding: utf-8 -*-
"""
Created on Thu May 14 17:21:15 2020

Runs the bot

@author: Guido Meijer
"""

import time
import tweepy
import pandas as pd
from joblib import load


def post_tweet(tweet_text, tweet_without_link, tweet_real, clf):

    # Post original tweet (with link)
    try:
        first_tweet = api.update_status(tweet_text)
    except:
        print('Tweet was already tweeted, abort!')
        return

    # Predict whether tweet is real or fake using the text without link
    prediction = clf.predict([tweet_without_link])[0]
    probability = clf.predict_proba([tweet_without_link])[0]

    # Post the prediction of the classifier
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

    # Post result
    if (prediction == 0) & (tweet_real == 0):
        api.update_status('I was right, this tweet was FAKE',
                          in_reply_to_status_id=second_tweet.id)
    elif (prediction == 1) & (tweet_real == 0):
        api.update_status('I was wrong, this tweet was FAKE',
                          in_reply_to_status_id=second_tweet.id)
    elif (prediction == 1) & (tweet_real == 1):
        api.update_status('I was right, this tweet was REAL',
                          in_reply_to_status_id=second_tweet.id)
    elif (prediction == 0) & (tweet_real == 1):
        api.update_status('I was wrong, this tweet was REAL',
                          in_reply_to_status_id=second_tweet.id)


def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id is not None:
        return False
    elif status.in_reply_to_screen_name is not None:
        return False
    elif status.in_reply_to_user_id is not None:
        return False
    else:
        return True


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):

        # Check if it's a posted by the user
        if from_creator(status):

            # Get the tweet text
            if 'extended_tweet' in status._json:
                tweet_text = status.extended_tweet['full_text']
            else:
                tweet_text = status.text

            # Remove weird & symbol text
            tweet_text = tweet_text.replace('&amp;', '&')

            # Remove any links
            no_link = list(filter(lambda x: 'http' not in x, tweet_text.split()))
            tweet_without_link = ' '.join(word for word in no_link)

            # Predict tweet
            clf = load('2020-05-14_SGD_model.joblib')
            if status.id_str == "25073877":
                print('Found new tweet from realDonaldTrump, re-tweeting..')
                post_tweet(tweet_text, tweet_without_link, 1, clf)
            if status.id_str == "19570960":
                print('Found new tweet from realDonaldTrFan, re-tweeting..')
                post_tweet(tweet_text, tweet_without_link, 0, clf)
            if status.id_str == "1407822289":
                print('Found new tweet from RealDonalDrumpf, re-tweeting..')
                post_tweet(tweet_text, tweet_without_link, 0, clf)


# Authenticate to Twitter
api_keys = pd.read_csv('D:\\Repositories\\Trump-tweets-classifier\\keys.csv')
auth = tweepy.OAuthHandler(api_keys['api_key'].values[0],
                           api_keys['api_key_secret'].values[0])
auth.set_access_token(api_keys['access_token'].values[0],
                      api_keys['access_token_secret'].values[0])

# Create API object
api = tweepy.API(auth)

# Load pre-trained classifier
clf = load('2020-05-14_SGD_model.joblib')

# Twitter ids
realDonaldTrump = "25073877"
realDonaldTrFan = "19570960"
RealDonalDrumpf = "1407822289"

# Start twitter stream
myStreamListener = MyStreamListener()
#myStreamListener = MyStreamListener(clf, realDonaldTrump, realDonaldTrFan, RealDonalDrumpf)
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(follow=[realDonaldTrump, realDonaldTrFan, RealDonalDrumpf])
