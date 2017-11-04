import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uszipcode import ZipcodeSearchEngine
import boto
import sys
import zipfile
import datetime

### Read Environmental Variables
AWS_ACCESS_KEY_ID = sys.argv[1]
AWS_SECRET_ACCESS_KEY = sys.argv[2]

### Data Ingestion

### Upload Output to AWS
output="clean_data.csv"
zipname='clean_data.zip'
#df_total.to_csv(output, index=False)
z=zipfile.ZipFile(zipname,"w")
z.write(output)
z.close()

connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

bucket_name = 'zillowdata-esrkoutput'

loc = boto.s3.connection.Location.DEFAULT

try:
    bucket = connection.create_bucket(bucket_name, location=loc)
except boto.exception.S3ResponseError as err:
    if "InvalidAccessKeyId" in err.code:
        "Invalid AWS key id"
    elif "SignatureDoesNotMatch" in err.code:
        "Invalid AWS secret key"
    else:
        print("Unexpected error:", sys.exc_info()[0])
except:
    print("Unexpected error:", sys.exc_info()[0])


s3key = boto.s3.key.Key(bucket)
s3key.key = zipname
s3key.set_contents_from_filename(zipname)
