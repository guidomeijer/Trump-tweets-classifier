# -*- coding: utf-8 -*-
"""
Created on Thu May 14 17:21:15 2020

This is a Twitter bot that scrapes new tweets from Donald Trump and two parody accounts
(@realDonaldTrFan and @RealDonalDrumpf). It runs the text of the tweet through a machine learning
algorithm that predicts whether the tweet was real or parody. It then tweets a thread of tweets:
the first one is the original text of the tweet and the second is whether the algorithm predicted
it right.

@author: Guido Meijer
"""

import datetime
import tweepy
from os import environ
from joblib import load


def post_tweet(tweet_text, tweet_real, prediction, probability):

    # Post original tweet
    try:
        first_tweet = api.update_status(tweet_text)
    except:
        print('Tweet was already tweeted, abort!')
        return

    # Post prediction of the classifier
    if (prediction == 0) & (tweet_real == 0):
        api.update_status(
            ('I predict this tweet is FAKE with a probability of %d%%.\n\nI was right, this tweet is FAKE.'
             % (probability * 100)), in_reply_to_status_id=first_tweet.id)
    elif (prediction == 1) & (tweet_real == 0):
        api.update_status(
            ('Fake news! I predict this tweet is REAL (%d%% probability) but it is actually FAKE.'
             % (probability * 100)), in_reply_to_status_id=first_tweet.id)
    elif (prediction == 1) & (tweet_real == 1):
        api.update_status(
            ('I predict this tweet is REAL with a probability of %d%%.\n\nI was right, this tweet is REAL.'
             % (probability * 100)), in_reply_to_status_id=first_tweet.id)
    elif (prediction == 0) & (tweet_real == 1):
        api.update_status(
            ('This is weird! This tweet looks FAKE to me (%d%% probability) but it is actually REAL!'
             % (probability * 100)), in_reply_to_status_id=first_tweet.id)


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

            # Predict whether tweet is real or fake using the text without link
            clf = load('2020-05-14_SGD_model.joblib')
            prediction = clf.predict([tweet_without_link])[0]
            probability = clf.predict_proba([tweet_without_link])[0]
            probability = probability[int(prediction)]

            # Filter out tweets that only have a link or are boring
            # (high probability of being real)
            if (len(no_link) > 0) and (((prediction == 1) & (probability < 0.9))
                                       or (prediction == 0)):
                if status.user.id_str == "25073877":
                    print('Found new tweet from realDonaldTrump, re-tweeting..')
                    post_tweet(tweet_text, 1, prediction, probability)
                if status.user.id_str == "19570960":
                    print('Found new tweet from realDonaldTrFan, re-tweeting..')
                    post_tweet(tweet_text, 0, prediction, probability)
                if status.user.id_str == "1407822289":
                    print('Found new tweet from RealDonalDrumpf, re-tweeting..')
                    post_tweet(tweet_text, 0, prediction, probability)


# Authenticate to Twitter
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_KEY_SECRET']
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

# Create API object
api = tweepy.API(auth)

# Twitter ids
realDonaldTrump = "25073877"
realDonaldTrFan = "19570960"
RealDonalDrumpf = "1407822289"

# Start twitter stream
print('Starting stream listener at %s'
      % str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(follow=[realDonaldTrump, realDonaldTrFan, RealDonalDrumpf])
