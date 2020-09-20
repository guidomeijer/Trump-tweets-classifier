import pandas as pd

keys = pd.DataFrame(index=[0], data={'access_token': '',
                                     'access_token_secret': '',
                                     'api_key': '',
                                     'api_key_secret': ''})
keys.to_csv('keys.csv')
