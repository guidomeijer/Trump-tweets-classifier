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


def get_prediction_tweet_text(prediction, probability, user_id, tweet_id):
    
    # Generate text of prediction
    if (prediction == 0) & (user_id == 19570960):
        pred_tweet_text = (('I predict this tweet is FAKE with a probability of %d%%. '
                           + 'I was right, this tweet is from the parody account '
                           + '@realDonaldTrFan. https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    elif (prediction == 1) & (user_id == 19570960):
        pred_tweet_text = (('I predict this tweet is REAL (%d%% probability) but '
                           + 'I was wrong! It is actually from the parody account '
                           + '@realDonaldTrFan. https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    elif (prediction == 0) & (user_id == 1407822289):
        pred_tweet_text = (('I predict this tweet is FAKE with a probability of %d%%. '
                           + 'I was right, this tweet is from the parody account '
                           + '@RealDonalDrumpf. https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    elif (prediction == 1) & (user_id == 1407822289):
        pred_tweet_text = (('I predict this tweet is REAL (%d%% probability) but '
                           + 'I was wrong! It is actually from the parody account '
                           + '@RealDonalDrumpf. https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    elif (prediction == 1) & (user_id == 25073877):
        pred_tweet_text = (('I predict this tweet is REAL with a probability of %d%%. '
                           + 'I was right, this tweet is from '
                           + '@realDonaldTrump. https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    elif (prediction == 0) & (user_id == 25073877):
        pred_tweet_text = (('I predict this tweet is FAKE (%d%% probability) '
                           + 'but I was wrong! It is from @realDonaldTrump himself. '
                           + 'https://twitter.com/user/status/%s')
                           % (probability * 100, tweet_id))
    return pred_tweet_text


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
            if 'extended_tweet' in status._json:
                tweet_text = status.extended_tweet['full_text']
            else:
                tweet_text = status.text

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
                    try:
                        first_tweet = api.update_status(tweet_text)
                    except:
                        print('Tweet was already tweeted, abort!')
                        return
                
                    # Post prediction of classifier as tweet
                    second_tweet_text = get_prediction_tweet_text(prediction,
                                                                  probability,
                                                                  status.user.id, 
                                                                  status.id)
                    api.update_status(second_tweet_text, in_reply_to_status_id=first_tweet.id)

                # If it's from Trump or realDonaldTrFan, post a reaction to his tweet
                if (status.user.id == 19570960) or (status.user.id == 25073877):
                    if np.mod(probs[0], 1) > 0.05:
                        reply_text = ('I give this tweet a %.1f out of 10 for absurdity.'
                                      % (probs[0] * 10))
                    else:
                        reply_text = ('I give this tweet a %d out of 10 for absurdity.'
                                      % np.round(probs[0] * 10))
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
