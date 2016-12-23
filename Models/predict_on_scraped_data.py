#scrape - tranform predict:
import os
import numpy as np
os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline
import pandas as pd
from sklearn.externals import joblib
from sklearn import metrics


data = cl_pipeline.get_data(site = "sfbay", area="sfc", category="apa", limit = 50)


data = data.drop_duplicates()
data["num_bed"] = data["num_bed"].astype("object")
data = cl_pipeline.clean_data(data)

data["num_bed"] = data["num_bed"].astype("str")


labels = pd.read_csv("labels.csv")
where_labels = labels["0"].values
bed_labels = ['1.0', '3.0', '2.0', '4.0', '5.0', 'Studio','8.0', '6.0', '7.0']


data = cl_pipeline.categorize(data, where_labels, bed_labels)


#this is needed for concatenate
data.index.name = None
data  = data.reset_index()

#need to load the categories here as well:
#load models:
vect  = joblib.load("count_vector.sav")
model = joblib.load("logit.sav")
X = cl_pipeline.generate_data(data = data, vect = vect)

data["prediction"] = model.predict(X)
data["diff"] = data["price"] - data["prediction"]
np.sqrt(metrics.mean_squared_error(data["price"], data["prediction"]))


data.sort_values("diff")
