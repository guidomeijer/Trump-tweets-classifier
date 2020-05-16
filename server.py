# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:11:19 2020

@author: Guido
"""

from os import environ
from flask import Flask

app = Flask(__name__)
app.run(environ.get('PORT'))
app.run(host= '0.0.0.0', port=environ.get('PORT'))
