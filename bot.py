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
import numpy as np
from os import environ
from joblib import load


def post_tweet(tweet_text, prediction, probability, user_id):

    # Post original tweet
    try:
        first_tweet = api.update_status(tweet_text)
    except:
        print('Tweet was already tweeted, abort!')
        return

    # Generate text of prediction
    if (prediction == 0) & (user_id == "19570960"):
        second_tweet_text = """I predict this tweet is FAKE with a probability of %d%%.\n\n
        I was right, this tweet is from the parody account @realDonaldTrFan.""" % (
                                                                        probability * 100)
    elif (prediction == 1) & (user_id == "19570960"):
        second_tweet_text = """Fake news! I predict this tweet is REAL (%d%% probability) but
        it is actually from the parody account @realDonaldTrFan.""" % (probability * 100)
    elif (prediction == 0) & (user_id == "1407822289"):
        second_tweet_text = """I predict this tweet is FAKE with a probability of %d%%.\n\n
        I was right, this tweet is from the parody account @RealDonalDrumpf.""" % (
                                                                        probability * 100)
    elif (prediction == 1) & (user_id == "1407822289"):
        second_tweet_text = """Fake news! I predict this tweet is REAL (%d%% probability) but
        it is actually from the parody account @RealDonalDrumpf.""" % (probability * 100)
    elif (prediction == 1) & (user_id == "25073877"):
        second_tweet_text = """I predict this tweet is REAL with a probability of %d%%.\n\n
        I was right, this tweet is from @realDonaldTrump himself.""" % (probability * 100)
    elif (prediction == 0) & (user_id == "25073877"):
        second_tweet_text = """This is weird! This tweet looks FAKE to me (%d%% probability)
        but it is actually from @realDonaldTrump!""" % (probability * 100)

    # Post prediction of classifier as tweet
    api.update_status(second_tweet_text, in_reply_to_status_id=first_tweet.id)


def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif hasattr(status, 'quoted_status'):
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

            # Skip tweets with links because they are mostly responses to what's in the link
            # and randomly skip 2/3 of the tweets to prevent tweeting too much and filling
            # everyones timeline
            if 'http' not in tweet_text and (np.random.randint(3) == 0):

                # Predict whether tweet is real or fake
                clf = load('2020-05-14_SGD_model.joblib')
                prediction = clf.predict([tweet_text])[0]
                probability = clf.predict_proba([tweet_text])[0]
                probability = probability[int(prediction)]

                # Filter out tweets that are boring (high probability of being real)
                if (((prediction == 1) & (probability < 0.9)) or (prediction == 0)):
                    if status.user.id_str == "25073877":
                        print('Found new tweet from realDonaldTrump, re-tweeting..')
                        post_tweet(tweet_text, prediction, probability, status.user.id_str)
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
