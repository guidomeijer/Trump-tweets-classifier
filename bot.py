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


def post_thread(tweet_id, prediction, probability, user_id):

    # Get entire thread
    reached_first = False
    thread_text = []
    while reached_first is False:
        status = api.get_status(tweet_id, tweet_mode='extended')
        tweet_text = status.full_text
        thread_text.append(tweet_text)
        if status.in_reply_to_status_id is None:
            reached_first = True
        else:
            tweet_id = status.in_reply_to_status_id

    # Post original thread of tweets
    for i in range(len(thread_text)-1, -1, -1):
        if i == len(thread_text)-1:
            try:
                posted_tweet = api.update_status(thread_text[i])
            except:
                print('Tweet was already tweeted, abort!')
                return
        else:
            try:
                posted_tweet = api.update_status(thread_text[i],
                                                 in_reply_to_status_id=posted_tweet.id)
            except:
                print('Tweet was already tweeted, abort!')
                return

    # Post prediction of classifier as tweet
    pred_tweet_text = get_prediction_tweet_text(prediction, probability, user_id)
    api.update_status(pred_tweet_text, in_reply_to_status_id=posted_tweet.id)


def is_tweet(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif hasattr(status, 'quoted_status'):
        return False
    elif status.in_reply_to_user_id == status.user.id:
        return True
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
                if (((prediction == 1) & (probability < 0.8)) or (prediction == 0)):

                    # Post tweet to timeline
                    if status.in_reply_to_user_id == status.user.id:
                        post_thread(status.id, prediction, probability, status.user.id_str)
                    else:
                        post_tweet(tweet_text, prediction, probability, status.user.id_str)

                    # If it's from Trump, post a reaction to his tweet
                    if status.user_id_str == "25073877":
                        reply_text = ('I am a machine learning algorithm and I give this tweet'
                                      + ' a %.1f out of 10 for absurdity') % (
                                                                      (1 - probs[1]) * 10)
                        api.update_status(reply_text, in_reply_to_status_id=status.id,
                                          auto_populate_reply_metadata=True)


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
