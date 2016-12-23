import os
import sqlite3
import numpy as np
import pandas as pd

from sklearn import metrics
from sklearn.externals import joblib
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Ridge, Lasso, LassoCV, RidgeCV
from sklearn.cross_validation import cross_val_score, KFold, train_test_split

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")

#OPTIONS:
area = "Brooklyn"
num_bed = "1.0"
num_listings =200


#build model:
data = pd.read_sql("select * from cl_housing_clean where area == ? and num_bed == ?",
                    conn, params = [area, num_bed]).reset_index()

data.shape


#categorize location and num_bed:
where_labels = list(data["where"].value_counts()[:40].index)
bed_labels = ['1.0', '3.0', '2.0', '4.0', '5.0', 'Studio','8.0', '6.0', '7.0']

data = cl_pipeline.categorize(data, where_labels, bed_labels)

vect = CountVectorizer(stop_words="english", min_df=15)
vect.fit(data["name"])


y = data["price"]
X = cl_pipeline.generate_data(data, vect)

X
#model:
model = Ridge(alpha = 1)
model.fit(X, y)

####
#scraping new data:
####

#setting a dict to transform to how cl likes the encoding:
city_dict = {'Brooklyn': 'newyorkbrk', 'Manhattan': 'newyorkmnh', 'San Francisco': 'sfbaysfc'}
site = city_dict[area][:-3]
area_short = city_dict[area][-3:]
category = "apa" if "San" in area else "abo"

data = cl_pipeline.get_data(site = site, area=area_short, category=category, limit = num_listings)

data

data = data.drop_duplicates()

data["num_bed"] = data["num_bed"].astype("object")
data = cl_pipeline.clean_data(data)

data["num_bed"] = data["num_bed"].astype("str")

data = data[data["num_bed"] == num_bed]

data = cl_pipeline.categorize(data, where_labels, bed_labels)




#this is needed for concatenate
data.index.name = None
data  = data.reset_index()

X = cl_pipeline.generate_data(data = data, vect = vect)



data["prediction"] = model.predict(X)
data["diff"] = data["price"] - data["prediction"]
np.sqrt(metrics.mean_squared_error(data["price"], data["prediction"]))

data["price"].std()

data.sort_values("diff")
