# Trump-tweets-classifier

This is a Twitter bot that scrapes new tweets from Donald Trump and two parody accounts (@realDonaldTrFan and @RealDonalDrumpf). It runs the text of the tweet through a machine learning algorithm that predicts whether the tweet was real or parody. It then tweets a thread of tweets: the first one is the original text of the tweet and the second one is the prediction of the algorithm and whether the algorithm predicted it right.

The machine learning algorithm is a support vector machine classifier using logistic regression as loss function. The classifier was trained on a training set consisting of 1000 real tweets and 1000 parody tweets (500 from each parody account). Classification accuracy is very high. Training the classifier on half of the dataset and predicting the other half yields an accuracy of 89% correct.

Want to set up your own Twitter bot? I followed these instructions: https://dev.to/emcain/how-to-set-up-a-twitter-bot-with-python-and-heroku-1n39
