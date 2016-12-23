#train a logistic model on some of the data (choose city and num beds) and save it:
import os
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
import sqlite3
from sklearn.cross_validation import cross_val_score, KFold, train_test_split
from sklearn.linear_model import Ridge, Lasso, LassoCV, RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score, KFold, train_test_split
from sklearn import metrics

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")

area = "Brooklyn"
num_bed = "1.0"

data = pd.read_sql("select * from cl_housing_clean where area == ? and num_bed == ?",
                    conn, params = [area, num_bed])

data = data.reset_index()

#categorize location and num_bed:
#these will be precomputed beforehand:
where_labels = list(data["where"].value_counts()[:40].index)
bed_labels = ['1.0', '3.0', '2.0', '4.0', '5.0', 'Studio','8.0', '6.0', '7.0']
pd.DataFrame(where_labels).to_csv("labels.csv")

data = cl_pipeline.categorize(data, where_labels, bed_labels)

vect = CountVectorizer(stop_words="english", min_df=10)
vect.fit(data["name"])

y = data["price"]

X = cl_pipeline.generate_data(data, vect)

#model:
#X_tr, X_val, y_tr, y_val = train_test_split(X, y, random_state = 3, test_size = 0.1)
model = Ridge(alpha = 1)
model.fit(X, y)


#preds = model.predict(X)
#np.sqrt(metrics.mean_squared_error(y, preds))

joblib.dump(model, "logit.sav")
joblib.dump(vect, "count_vector.sav")

np.sqrt(metrics.mean_squared_error(y, preds))
