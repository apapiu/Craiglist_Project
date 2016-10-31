#Ml for craiglist data:

import os
import pandas as pd
import numpy as np
import sqlite3
from sklearn.linear_model import Ridge, Lasso
from sklearn.cross_validation import cross_val_score, KFold

from sklearn.feature_extraction.text import TfidfVectorizer

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")
data = pd.read_sql("select * from cl_housing_clean", conn)
conn.close()

data = data.drop(["id", "id.1"],axis = 1 )

y = data.price
data["where"][data["where"].isnull()] = "Other"


pop_nbd = data["where"].value_counts().head(50).index



nbds = data["where"]

good_nbds = []

for loc in nbds:
    if loc in pop_nbd:
        good_nbds.append(loc)
    else:
        for pop_loc in pop_nbd:
            c = 0
            if pop_loc in loc:
                good_nbds.append(pop_loc)
                c = c+1
                break
        if c == 0:
            good_nbds.append("Other")
 
data.loc[:,"where"] = good_nbds

val = data.sort_values("datetime")[:5000]
train = data.sort_values("datetime")[5000:]

y_train = y[5000:]

data_cat =pd.get_dummies(data[["num_bed", "where", "area"]])
X_cat = data_cat[5000:]
#a look at the bags of words:

vect = TfidfVectorizer(stop_words="english", min_df=2)
X = vect.fit_transform(train.name)

vect.get_feature_names()

X_total = np.hstack([X.toarray(), X_cat])

model = Ridge()
model.fit(X_total, y_train)

pd.Series(model.coef_, index = vect.get_feature_names()).sort_values()
#the coefficients don't make much sense...

folds = KFold(n = train.shape[0],  n_folds=5)
np.sqrt(-cross_val_score(model, X, y_train, scoring = "mean_squared_error", cv = folds))

