#scrape one listing and get it in shape for prediction:
import requests
import re
import sqlite3
import seaborn as sns
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import scipy.stats as stats

os.chdir("/Users/alexpapiu/Documents/Craiglist_Project")
import cl_pipeline

conn = sqlite3.connect("/Users/alexpapiu/Documents/Data/Craigslist/housing.db")

#this is just so we have know what the df looks like:
data = pd.read_sql("select * from cl_housing limit 1", conn)


link = "https://sfbay.craigslist.org/sfc/apa/5922247127.html"
html = requests.get(link).text
soup = BeautifulSoup(html, "html.parser")

#get new data:
housing = soup.find("span", class_ = "housing").text

data["num_bed"] = re.search("(\d)br", housing).group(1)
data["sq_feet"] = re.search("(\d*)ft", housing).group(1)
data["name"] = soup.find("span", id = "titletextonly").text
data["price"] = soup.find("span", class_ = "price").text
data["where"] = soup.find("small").text

data = cl_pipeline.clean_data(data)

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
