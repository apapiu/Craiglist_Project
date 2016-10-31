import sys
sys.path.insert(0, '/Users/alexpapiu/Documents/Craiglist_Project')
import cl_pipeline

listing_number = int(sys.argv[1])

cl_pipeline.data_to_sql(listing_number)
