#the pipeline for craigslist:

import pandas as pd
import numpy as np
import os
from craigslist import CraigslistHousing
import schedule
import time
import datetime
import sqlite3

#functions:

#scrape the data and return a pandas df:
def get_data(site = "newyork", area = None, category = "abo", limit = 25):
    cl = CraigslistHousing(site=site, area=area, category=category)
    results = cl.get_results(sort_by='newest', limit = limit)
    
    data = pd.DataFrame(results)
    data.index = data["id"]
    
    data["area"] = site + area if area else site
    return(data)
    

#get data from multiple sources, concatenate it and write csv:
def write_data(limit = 25):
    timez = time.strftime("%Y-%m-%d %H:%M:%S")
    
    data = pd.concat([get_data(area = "brk", limit = limit),
                      get_data(area = "mnh", limit = limit),
                      get_data(site = "sfbay", area="sfc", category="apa", limit = limit)])
    
    link = "/Users/alexpapiu/Documents/Data/Craigslist/data_nyc_" + timez + ".csv"
    link = link.replace(" ", "")
    data.to_csv(link)
    
#get df and insert it in a sqlite database:
def data_to_sql(limit = 25):
    
    os.chdir("/Users/alexpapiu/Documents/Data/Craigslist")
    data = pd.concat([get_data(area = "brk", limit = limit),
                      get_data(area = "mnh", limit = limit),
                      get_data(site = "sfbay", area="sfc", category="apa", limit = limit)])
                      
    conn = sqlite3.connect("housing.db")
    data.to_sql("cl_housing", con = conn,  index = False, if_exists="append")
    conn.close()

#data_to_sql(2500)

#clean function:
def clean_data(data):
    data.datetime = pd.to_datetime(data.datetime)
    data["sq_feet"] = data["sq_feet"].astype(float)
    
    data = (data.dropna(subset = ["price"]) # eliminate things with no price
                .assign(price = data["price"].str.lstrip("$").astype(float)) #make the price numeric
                .query("price > 100 & price < 30000") #eliminate crazy prices
                .assign(name = data["name"].str.replace("/", " ")) #replace "/" with " "
                .assign(hour = data["datetime"].dt.hour, #extract time feats
                        dayofweek = data["datetime"].dt.dayofweek))
    
    data.loc[data["num_bed"].isin(["5", "6", "7", "8"]), "num_bed"] = "5 or more" #coalesce high num_bed
    
    data["name"] = data["name"].str.lower()
    data.loc[data["name"].str.contains("studio"), "num_bed"] = "Studio" #if num_bed is unknown and contains studio
    
    data["where"] = (data["where"].str.lower()
                                  .str.replace("no fee", ""))                                 
    
    data["int_bed"] = data["num_bed"]
    data.loc[data.int_bed == "Studio", "int_bed"] = 1
    data.loc[data.int_bed == "5 or more", "int_bed"] = 5

    data["int_bed"] = data["int_bed"].astype(float)
    data["per_person"] = data["price"]/data["int_bed"]
    return(data)
    
    #loc_count = data["where"].value_counts() #reducing levels
    #mask = data["where"].isin(loc_count[loc_count < 5].index)
    #data.ix[mask, "where"] = "other" #replace  rare locations with "other"

def create_matrices(data, data_val): #this is tricky with a validation set.
    
    all_data = pd.concat([data, data_val],1)
    
    data_cat = pd.get_dummies(data[["where", "hour", "dayofweek"]])
    feats = data_cat.columns
    data_cat = sparse.csr_matrix(data_cat.values)

    vect = CountVectorizer(stop_words="english", min_df = 1, ngram_range=(1,2))
    data_text = vect.fit_transform(data["name"])
    
    X = sparse.hstack((data_cat, data_text))
    feats = np.hstack((feats, vect.get_feature_names()))
    y = data.price

    return(X, y, feats)
