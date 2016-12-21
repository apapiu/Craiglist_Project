import os
import re
import requests
import sqlite3

import seaborn as sns
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from flask import Flask

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline


conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")

#this is just so we have know what the df looks like:
data = pd.read_sql("select * from cl_housing limit 100", conn)

app = Flask(__name__)

data["price"]

@app.route('/')
@app.route('/hello')
def HelloWorld():
    x =
    return " ".join(data["price"])

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
