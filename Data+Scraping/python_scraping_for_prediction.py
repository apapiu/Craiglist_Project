#scrape one listing and get it in shape for prediction:
import requests
import re
import os
import sqlite3
import seaborn as sns
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")

#this is just so we have know what the df looks like:
data = pd.read_sql("select * from cl_housing limit 1", conn)


#to keep track of categories:
cstore = pd.HDFStore('temp_cat_data.h5', mode='w')
data = cstore.select("temp_cat_data", stop = 10)
data

data.num_bed

data.dtypes


keep_data = data
data.dtypes

link = "http://sfbay.craigslist.org/sfc/apa/5883019817.html"
html = requests.get(link).text
soup = BeautifulSoup(html, "html.parser")

#get new data:
housing = soup.find("span", class_ = "housing").text
data.loc[0,"num_bed"]

data.loc[0,"num_bed"] = re.search("(\d)br", housing).group(1) + ".0"


try:
    data.loc[0, "sq_feet"] = re.search("(\d*)ft", housing).group(1)

data.loc[0,"name"] = soup.find("span", id = "titletextonly").text
data.loc[0,"price"] = soup.find("span", class_ = "price").text


data.loc[0,"where"] = soup.find("small").text


data.dtypes

data = clean_data(data)
data.dtypes

#make prediction:

#load models:
vect  = joblib.load("count_vector.sav")
model = joblib.load("logit.sav")
X = generate_data(data = data)

data["prediction"] = model.predict(X)
data["prediction"]

data["diff"] = data["price"] - data["prediction"]


#looking up information about the neighborhood in the database:
location = data.loc[0, "where"]
query = 'select * from cl_housing_clean where "where" = ?'
local_data = pd.read_sql(query, conn, params= [location])

price = data["price"][0]

local_data.query("num_bed == '1.0'").loc[:,"price"].hist(bins = 10)

plt.axvline(data["price"][0], color='r')

percentile = stats.percentileofscore(local_data["price"], price)
percentile = np.round(percentile, 0)

print("The listing is cheaper than {0} percent of all other 1 bedrooms in {1}!".format(100 - percentile, location))
