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


# Check every INTERVAL seconds for new tweets
INTERVAL = 60

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

# Initialize variables
last_real_id = 0
last_fake1_id = 0
last_fake2_id = 0

# Start bot
while True:

    # Time-out
    time.sleep(INTERVAL)
    print('Checking for new tweets..')

    # Check for new tweets from @realDonaldTrump
    if last_real_id == 0:
        new_real_tweet = api.user_timeline(screen_name='realDonaldTrump', count=1,
                                           include_rts=False, tweet_mode='extended',
                                           exclude_replies=True)
    else:
        new_real_tweet = api.user_timeline(screen_name='realDonaldTrump', count=1,
                                           include_rts=False, tweet_mode='extended',
                                           exclude_replies=True, max_id=last_real_id)

    # Check if the tweet is a retweet and it's new
    if len(new_real_tweet) > 0:
        if new_real_tweet[0].id != last_real_id:
            # Filter out any links
            tweet_text = new_real_tweet[0].full_text
            no_link = list(filter(lambda x: 'http' not in x, tweet_text.split()))
            tweet_without_link = ' '.join(word for word in no_link)

            # Post tweet
            print('Found new tweet from realDonaldTrump, re-tweeting..')
            last_real_id = new_real_tweet[0].id
            post_tweet(tweet_text, tweet_without_link, 1, clf)

    # Check for new tweets from @realDonaldTrFan
    if last_fake1_id == 0:
        new_fake1_tweet = api.user_timeline(screen_name='realDonaldTrFan', count=1,
                                            include_rts=False, tweet_mode='extended',
                                            exclude_replies=True)
    else:
        new_fake1_tweet = api.user_timeline(screen_name='realDonaldTrFan', count=1,
                                            include_rts=False, tweet_mode='extended',
                                            exclude_replies=True, max_id=last_fake1_id)

    # Check if the tweet is a retweet and it's new
    if len(new_fake1_tweet) > 0:
        if new_fake1_tweet[0].id != last_fake1_id:
            # Filter out any links
            tweet_text = new_fake1_tweet[0].full_text
            no_link = list(filter(lambda x: 'http' not in x, tweet_text.split()))
            tweet_without_link = ' '.join(word for word in no_link)

            # Post tweet
            print('Found new tweet from realDonaldTrFan, re-tweeting..')
            last_fake1_id = new_fake1_tweet[0].id
            post_tweet(tweet_text, tweet_without_link, 0, clf)

    # Check for new tweets from @RealDonalDrumpf
    if last_fake2_id == 0:
        new_fake2_tweet = api.user_timeline(screen_name='RealDonalDrumpf', count=1,
                                            include_rts=False, tweet_mode='extended',
                                            exclude_replies=True)
    else:
        new_fake2_tweet = api.user_timeline(screen_name='RealDonalDrumpf', count=1,
                                            include_rts=False, tweet_mode='extended',
                                            exclude_replies=True, max_id=last_fake2_id)

    # Check if the tweet is a retweet and it's new
    if len(new_fake2_tweet) > 0:
        if new_fake2_tweet[0].id != last_fake2_id:
            # Filter out any links
            tweet_text = new_fake2_tweet[0].full_text
            no_link = list(filter(lambda x: 'http' not in x, tweet_text.split()))
            tweet_without_link = ' '.join(word for word in no_link)

            # Post tweet
            print('Found new tweet from realDonaldTrFan, re-tweeting..')
            last_fake2_id = new_fake2_tweet[0].id
            post_tweet(tweet_text, tweet_without_link, 0, clf)
