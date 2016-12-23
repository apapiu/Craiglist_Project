#the pipeline for craigslist:
import pandas as pd
import numpy as np
import os
from craigslist import CraigslistHousing
import schedule
import time
import datetime
import sqlite3

from sklearn.linear_model import Ridge, Lasso, LassoCV, RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score, KFold, train_test_split
from sklearn import metrics

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


#main functions:

def get_data(site = "newyork", area = None, category = "abo", limit = 25, geotagged = True):
    """ scrape the data and return a pandas df """

    cl = CraigslistHousing(site=site, area=area, category=category)
    results = cl.get_results(sort_by='newest', limit = limit, geotagged = geotagged)

    data = pd.DataFrame(results)
    data.index = data["id"]

    data["area"] = site + area if area else site
    return(data)



def write_data(limit = 25):
    """get data from multiple sources, concatenate it and write csv"""

    timez = time.strftime("%Y-%m-%d %H:%M:%S")

    data = pd.concat([get_data(area = "brk", limit = limit),
                      get_data(area = "mnh", limit = limit),
                      get_data(site = "sfbay", area="sfc", category="apa", limit = limit)])

    link = "/Users/alexpapiu/Documents/Data/Craigslist/data_nyc_" + timez + ".csv"
    link = link.replace(" ", "")
    data.to_csv(link)

def data_to_sql(limit = 25):
    """get df and insert it in a sqlite database """


    os.chdir("/Users/alexpapiu/Documents/Data/Craigslist")
    data = pd.concat([get_data(area = "brk", limit = limit),
                      get_data(area = "mnh", limit = limit),
                      #get rooms too:
                      get_data(area = "brk", category = "roo?bundleDuplicates=1&availabilityMode=0"),
                      get_data(area = "mnh", category = "roo?bundleDuplicates=1&availabilityMode=0"),
                      get_data(site = "sfbay", area="sfc", category="apa", limit = limit)])

    conn = sqlite3.connect("housing.db")
    data.to_sql("cl_housing", con = conn, index = False, if_exists="append")
    conn.close()

#data_to_sql(2500)


def clean_data(data):
    data = data.drop_duplicates()

    data.datetime = pd.to_datetime(data.datetime)
    data["sq_feet"] = data["sq_feet"].astype(float)

    data = (data.dropna(subset = ["price"]) # eliminate things with no price
                .assign(price = data["price"].str.lstrip("$").astype(float)) #make the price numeric
                .query("price > 100 & price < 30000") #eliminate crazy prices
                .assign(name = data["name"].str.replace("/", " ")) #replace "/" with " "
                .assign(hour = data["datetime"].dt.hour, #extract time feats
                        dayofweek = data["datetime"].dt.dayofweek))

    #data.loc[data["num_bed"].isin(["5", "6", "7", "8"]), "num_bed"] = "5 or more" #coalesce high num_bed

    data["name"] = data["name"].str.lower()
    data.loc[data["name"].str.contains("studio"), "num_bed"] = "Studio" #if num_bed is unknown and contains studio

    data["where"] = (data["where"].str.lower()
                                  .str.replace("no fee", ""))

    #make area prettier:
    city_clean_dict = {"newyorkbrk":"Brooklyn", "newyorkmnh":"Manhattan", "sfbaysfc":"San Francisco"}
    data["area"] = data["area"].map(city_clean_dict)


    try:
        data = data.drop("id.1", 1)
    except:
        pass

    #cleaning up the neighborhood:
    data["where"] = (data["where"].str.replace(r"[^\w\s-]", " ")
                              .str.replace(" +", " ")
                              .str.strip())

    data["int_bed"] = data["num_bed"]
    data.loc[data.int_bed == "Studio", "int_bed"] = 1
    data.loc[data.int_bed == "5 or more", "int_bed"] = 5

    data["int_bed"] = data["int_bed"].astype(float)
    data["per_person"] = data["price"]/data["int_bed"]
    return(data)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#models and data preprocessing:


#makes the dataframes ready for get_dummies:
def categorize(data, where_labels, bed_labels):
    data["where"] = data["where"].astype("object")
    data["where"] = data["where"].astype("category", categories = where_labels)
    data["num_bed"] = data["num_bed"].astype("category", categories = bed_labels)
    return(data)


def generate_data(data, vect):

    cols = ["has_image", "num_bed", "where", "hour", "dayofweek"]
    data_num = data[cols]
    X_num = pd.get_dummies(data_num)

    #text:
    X_text = vect.transform(data["name"])
    X_text = pd.DataFrame(X_text.toarray(), columns = vect.get_feature_names())
    X = pd.concat((X_num, X_text), 1)
    return(X)
