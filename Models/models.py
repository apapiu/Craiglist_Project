import os

import pandas as pd
import numpy as np
import sqlite3
from sklearn.linear_model import Ridge, Lasso, LassoCV, RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score, KFold, train_test_split
from sklearn import metrics

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

%matplotlib inline

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")
data = pd.read_sql("select * from cl_housing_clean", conn)
conn.close()

data = data.drop(["id"], axis = 1)


data = data.query("price < 10000 & area == 'San Francisco' & int_bed == 1")
data = data.reset_index()

data.head()

data["where"] = data["where"].fillna("other")


cols = ["has_image", "num_bed", "where", "hour", "dayofweek"]
data_num = data[cols]

data_num

data["where"].value_counts()


from sklearn.preprocessing import OneHotEncoder, LabelEncoder
loc_label = LabelEncoder()
loc_enc = OneHotEncoder()
num_bed_enc = OneHotEncoder()

temp = ["cat", "dog", "cat"]

loc_label.fit(temp)

loc_label.transform(["hey"])







X_num = pd.get_dummies(data[cols])
y = data["price"]

X_num


data["where"] = data["where"].fillna("Other")

from sklearn.preprocessing import OneHotEncoder, LabelEncoder
loc_label = LabelEncoder()
loc_enc = OneHotEncoder()
num_bed_enc = OneHotEncoder()

where_enc = loc_label.fit_transform(data["where"])
X_where = loc_enc.fit_transform(loc_label.fit_transform(data["where"]))


X_num

X_num

X_tr, X_val, y_tr, y_val = train_test_split(X_num, y, random_state = 3)

model = Ridge(alpha = 1)
#model = RandomForestRegressor(n_estimators = 100)



model.fit(X_tr, y_tr)
#model.fit(X_tr, np.log1p(y_tr))





preds = model.predict(X_val)


naive_preds = np.repeat(np.mean(y_tr), X_val.shape[0])

np.sqrt(metrics.mean_squared_error(y_val, naive_preds))
np.sqrt(metrics.mean_squared_error(y_val, preds))
#np.sqrt(-cross_val_score(model, X_tr, y_tr, scoring = "mean_squared_error"))


#618 with Ridge
#653 with Random Forest
#with the added bag of words:

text = data["name"]

vect = CountVectorizer(stop_words="english", min_df=5)
X = vect.fit_transform(text)

X = pd.DataFrame(X.toarray(), columns = vect.get_feature_names())
X



X_all = pd.concat((X, X_num), 1)




X_tr, X_val, y_tr, y_val = train_test_split(X_all, y, random_state = 3)


model = Ridge(alpha = 1)

#model = RidgeCV()
#model = LassoCV()
#model = RandomForestRegressor(n_estimators = 100)

model.fit(X_tr, y_tr)

#model.fit(X_tr, np.log1p(y_tr))




preds = model.predict(X_val)

naive_preds = np.repeat(np.mean(y_tr), X_val.shape[0])

np.sqrt(metrics.mean_squared_error(y_val, naive_preds))
np.sqrt(metrics.mean_squared_error(y_val, preds))

coeffs = pd.Series(model.coef_, index = X_all.columns)

coeffs.sort_values()
