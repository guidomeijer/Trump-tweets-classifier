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


def get_prediction_tweet_text(prediction, probability, user_id):

    # Generate text of prediction
    if (prediction == 0) & (user_id == "19570960"):
        pred_tweet_text = ('I predict this tweet is FAKE with a probability of %d%%.\n\n'
                           + 'I was right, this tweet is from the parody account '
                           + '@realDonaldTrFan.') % (probability * 100)
    elif (prediction == 1) & (user_id == "19570960"):
        pred_tweet_text = ('Fake news! I predict this tweet is REAL (%d%% probability) but '
                           + 'it is actually from the parody account '
                           + '@realDonaldTrFan.') % (probability * 100)
    elif (prediction == 0) & (user_id == "1407822289"):
        pred_tweet_text = ('I predict this tweet is FAKE with a probability of %d%%.\n\n'
                           + 'I was right, this tweet is from the parody account '
                           + '@RealDonalDrumpf.') % (probability * 100)
    elif (prediction == 1) & (user_id == "1407822289"):
        pred_tweet_text = ('Fake news! I predict this tweet is REAL (%d%% probability) but '
                           + 'it is actually from the parody account '
                           + '@RealDonalDrumpf.') % (probability * 100)
    elif (prediction == 1) & (user_id == "25073877"):
        pred_tweet_text = ('I predict this tweet is REAL with a probability of %d%%.\n\n'
                           + 'I was right, this tweet is from '
                           + '@realDonaldTrump himself.') % (probability * 100)
    elif (prediction == 0) & (user_id == "25073877"):
        pred_tweet_text = ('This is weird! This tweet looks FAKE to me (%d%% probability) '
                           + 'but it is really from @realDonaldTrump!') % (probability * 100)
    return pred_tweet_text


def get_reply_text(probability):

    # Generate text of prediction
    if probability < 0.1:
        reply_tweet_text = 'I am a bot and this tweet looks perfectly normal to me.'
    elif (probability > 0.1) & (probability < 0.2):
        reply_tweet_text = ('I am a bot and I think this tweet is not completely normal.')
    elif (probability > 0.2) & (probability < 0.3):
        reply_tweet_text = ('I am an algoritm and I classify this tweet as "slightly absurd".')
    elif (probability > 0.3) & (probability < 0.4):
        reply_tweet_text = ('This tweet looks absurd to me! But what do I know, '
                            + 'I am just a bot.\n\nFollow me for more funny predictions :)')
    elif (probability > 0.4) & (probability < 0.5):
        reply_tweet_text = ('I am a machine learning algorithm, I did the math and my numbers '
                            + 'tell me that this tweet is very wacky!\n\nFollow me for more '
                            + 'funny predictions.')
    elif (probability > 0.5) & (probability < 0.6):
        reply_tweet_text = ('Wow, this tweet is absurd! Even I can see it, and I am just a bot.'
                            + '\n\nFollow me for more funny predictions!')
    elif (probability > 0.6) & (probability < 0.7):
        reply_tweet_text = ('I am a machine learning algorithm and my calculations tell me that '
                            + 'what Trump is saying here is completely bonkers!\n\n'
                            + 'Follow me for more funny predictions.')
    elif (probability > 0.7) & (probability < 0.8):
        reply_tweet_text = ('What Trump is saying here is ludicrous! I am a machine learning '
                            + 'algorithm and I give this tweet a whopping %.1f on the '
                            + 'absurd-o-meter!\n\nFollow me for more funny predictions.') % (
                                                                      probability * 10)
    elif (probability > 0.8) & (probability < 0.9):
        reply_tweet_text = ('I did the math and this tweet is completely bat-shit crazy! '
                            + 'It scores a %.1f out of 10 for absurdity!'
                            + '\n\nI am a bot, follow me for more funny predictions.') % (
                                                                      probability * 10)
    elif (probability > 0.9) & (probability < 1):
        reply_tweet_text = ('WHAT TRUMP IS SAYING HERE IS COMPLETELY IDIOTIC! IT SCORES A '
                            + '%.1f ON THE ABSURD-O-METER!\n\n'
                            + 'I am a bot, follow me for more funny predictions.') % (
                                                                      probability * 10)
    return reply_tweet_text


def post_tweet(tweet_text, prediction, probability, user_id):

    # Post original tweet
    try:
        first_tweet = api.update_status(tweet_text)
    except:
        print('Tweet was already tweeted, abort!')
        return

    # Post prediction of classifier as tweet
    second_tweet_text = get_prediction_tweet_text(prediction, probability, user_id)
    api.update_status(second_tweet_text, in_reply_to_status_id=first_tweet.id)


def get_tweet_text(status):
    if 'extended_tweet' in status._json:
        tweet_text = status.extended_tweet['full_text']
    else:
        tweet_text = status.text
    return tweet_text


def is_tweet(status):
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

        # Check if it's an original post and not a retweet, reply or quote
        if is_tweet(status):

            # Get the tweet text
            tweet_text = get_tweet_text(status)

            # Remove weird & symbol text
            tweet_text = tweet_text.replace('&amp;', '&')

            # Skip tweets with links because they are mostly responses to what's in the link
            # Skip tweets that end with .. because they are usually a thread
            if ('http' not in tweet_text) and (tweet_text[-2:] != '..'):

                # Predict whether tweet is real or fake
                clf = load('2020-05-14_SGD_model.joblib')
                prediction = clf.predict([tweet_text])[0]
                probs = clf.predict_proba([tweet_text])[0]
                probability = probs[int(prediction)]

                # Filter out tweets that are boring (high probability of being real)
                # and only post one out of three tweets to prevent filling everybody's timeline
                if ((((prediction == 1) & (probability < 0.8)) or (prediction == 0))
                        and (np.random.randint(3) == 0)):

                    # Post tweet to timeline
                    post_tweet(tweet_text, prediction, probability, status.user.id_str)

                # If it's from realDonaldTrFan, post a reaction to his tweet
                if (status.user.id == 19570960) or (status.user.id == 25073877):
                    reply_text = ('I am a bot and I give this tweet'
                                  + ' a %.1f out of 10 for absurdity.\n\n'
                                  + 'Follow me for more funny predictions!') % (probs[0] * 10)
                    api.update_status(reply_text, in_reply_to_status_id=status.id,
                                      auto_populate_reply_metadata=True)

                """
                # If it's from Trump, post a reaction to his tweet
                if status.user.id == 25073877:
                    reply_text = get_reply_text(probs[0])
                    api.update_status(reply_text, in_reply_to_status_id=status.id,
                                      auto_populate_reply_metadata=True)
                """


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
