import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import boto

### Read Environmental Variables
AWS_ACCESS_KEY_ID = sys.argv[1]
AWS_SECRET_ACCESS_KEY = sys.argv[2]
zipname='properties_2016.csv'
### Data Ingestion

# First import the properties files
df16 = pd.read_csv('properties_2016.csv', low_memory=False)

connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

bucket_name = 'zillowdataesrk'

loc = boto.s3.connection.Location.DEFAULT


bucket = connection.create_bucket(bucket_name, location=loc)
#except boto.exception.S3ResponseError as err:
 #   if "InvalidAccessKeyId" in err.code:
  #      "Invalid AWS key id"
   # elif "SignatureDoesNotMatch" in err.code:
    #    "Invalid AWS secret key"
    #else:
     #   print("Unexpected error:", sys.exc_info()[0])
#except:
 #   print("Unexpected error:", sys.exc_info()[0])


s3key = boto.s3.key.Key(bucket)
s3key.key = zipname
s3key.set_contents_from_filename(zipname)