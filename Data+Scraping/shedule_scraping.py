#setting up a timer:

import schedule
import time
import pandas
import datetime
from craigslist import CraigslistHousing



write_data()

schedule.every(10).minutes.do(write_data)

while 1:
    schedule.run_pending()
    time.sleep(1)

