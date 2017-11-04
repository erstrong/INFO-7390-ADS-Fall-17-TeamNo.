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

# First import the properties files
df16 = pd.read_csv('properties_2016.csv', low_memory=False)
df17 = pd.read_csv('properties_2017.csv', low_memory=False)

# Then import the transaction data
df_transactions16 = pd.read_csv('train_2016_v2.csv', low_memory=False)
df_transactions17 = pd.read_csv('train_2017.csv', low_memory=False)

# Next match the properties to transactions on ParcelID, using a right join
df_merged16 = pd.merge(df16, df_transactions16, on='parcelid', how='right')
df_merged17 = pd.merge(df17, df_transactions17, on='parcelid', how='right')

## Latitude and Longitude
# Drop all NAs since we will need to use accurate coordinates in Part 4 and thus should not
# fill missing values.

df_merged16 = df_merged16.dropna(subset=['latitude'])
df_merged16 = df_merged16.dropna(subset=['longitude'])
df_merged17 = df_merged17.dropna(subset=['latitude'])
df_merged17 = df_merged17.dropna(subset=['longitude'])



# Combine the two data sets
df_merged16['setyear'] = 2016
df_merged17['setyear'] = 2017
df_total = df_merged16.append(df_merged17, ignore_index=True)

### Data Cleanup

## Latitude and longitude
# The values are missing decimal points. Transform each column by dividing by 1000000.
df_total['latitude'] = df_total['latitude'] / 1000000
df_total['longitude'] = df_total['longitude'] / 1000000


## Tax Delinquency Years
def convertyears(x):
    if x > 9 and x < 20:
        t = '20' + str(x)
        return float(t)
    elif x <= 9:
        t = '200' + str(x)
        return float(t)
    elif x > 20:
        t = '19' + str(x)
        return float(t)
    else:
        return np.nan

df_total['taxdelinquencyyear'] = df_total['taxdelinquencyyear'].map(lambda a: convertyears(a))

## Transaction Date
format = '%Y-%m-%d'
df_total['transactiondate'] = df_total['transactiondate'].map(lambda a: datetime.datetime.strptime(a, format))


## Pool Types Column
df_total['poolcnt'].fillna(0, inplace=True)
df_total['hashottuborspa'].fillna(False, inplace=True)

def pooltypes(a, b):
    if a and b > 0:
        return 2
    elif not(a) and b > 0:
        return 7
    elif a and b == 0:
        return 10
    else:
        return 0

df_total['pooltype'] = df_total.apply(lambda x: pooltypes(x['hashottuborspa'], x['poolcnt']), axis=1)

## Zip Codes
search = ZipcodeSearchEngine()
zips=pd.DataFrame(columns=["parcelid","zipcode"])

def zip(a, b):
    c = search.by_coordinate(a,b)
    return c[0].Zipcode

df_total['zipcode'] = df_total.apply(lambda x: zip(x['latitude'], x['longitude']), axis=1)

## Census Tracts and Blocks
df_total['rawcensustractandblock'].fillna(0, inplace = True)
def census(a):
    return int(round(a * 1000000))

df_total['rawcensustractandblock'] = df_total['rawcensustractandblock'].map(lambda a: census(a))

#df_total.reset_index()

#### Remove data we will not be using based on the EDA

# Columns with >80% missing data that cannot be calculated or are redundant

df_total.drop('architecturalstyletypeid', axis=1, inplace=True)
df_total.drop('basementsqft', axis=1, inplace=True)
df_total.drop('buildingclasstypeid', axis=1, inplace=True)
df_total.drop('decktypeid', axis=1, inplace=True)
df_total.drop('finishedfloor1squarefeet', axis=1, inplace=True)
df_total.drop('finishedsquarefeet12', axis=1, inplace=True)
df_total.drop('finishedsquarefeet13', axis=1, inplace=True)
df_total.drop('finishedsquarefeet15', axis=1, inplace=True)
df_total.drop('finishedsquarefeet50', axis=1, inplace=True)
df_total.drop('finishedsquarefeet6', axis=1, inplace=True)
df_total.drop('poolsizesum', axis=1, inplace=True)
df_total.drop('storytypeid', axis=1, inplace=True)
df_total.drop('typeconstructiontypeid', axis=1, inplace=True)
df_total.drop('yardbuildingsqft17', axis=1, inplace=True)
df_total.drop('yardbuildingsqft26', axis=1, inplace=True)
df_total.drop('threequarterbathnbr', axis=1, inplace=True)
df_total.drop('censustractandblock', axis=1, inplace=True)
df_total.drop('bathroomcnt', axis=1, inplace=True)
df_total.drop('pooltypeid7',axis=1, inplace=True)
df_total.drop('pooltypeid2',axis=1, inplace=True)
df_total.drop('pooltypeid10',axis=1, inplace=True)
df_total.drop('regionidzip',axis=1, inplace=True)
df_total.drop('regionidneighborhood',axis=1, inplace=True)
df_total.drop('regionidcounty',axis=1, inplace=True)
df_total.drop('propertyzoningdesc',axis=1, inplace=True)


#### Missing Values

# airconditioningtypid use 5: None
df_total['airconditioningtypeid'].fillna(5, inplace=True)

# fireplacecnt is at the threshold for the missing data cutoff but since there are no 0s, we
# assume that missing values are 0s.
df_total['fireplacecnt'].fillna(0, inplace=True)

# Calculate the missing valeus for fireplaceflag from fireplacecnt
# Currently where there is a value it is "true", we will change this
df_total['fireplaceflag'] = False
df_total.loc[df_total['fireplacecnt'] > 0, 'fireplaceflag'] = True




# Garages
df_total['garagecarcnt'].fillna(0, inplace=True)

# Find the square footage median before filling NAs with 0s
value=df_total['garagetotalsqft'].median()

# We have decided to assume that garagecarcnt is accurate when it has a count but garagetotalsqft is 0
df_total['garagetotalsqft']=df_total['garagetotalsqft'].replace(float(0),np.nan)

m1=(df_total['garagecarcnt']>0.0)
m2=(df_total['garagecarcnt']==0.0)

df_total.loc[m1,'garagetotalsqft']=df_total.loc[m1,'garagetotalsqft'].fillna(value)
df_total.loc[m2,'garagetotalsqft']=df_total.loc[m2,'garagetotalsqft'].fillna(0.0)


# Median and Mode Replacements
# Data is skewed so use median rather than mean for anything that is a count

df_total['bedroomcnt'].fillna(df_total['bedroomcnt'].median(), inplace=True)
df_total['buildingqualitytypeid'].fillna(df_total['buildingqualitytypeid'].mean(), inplace=True)
df_total['calculatedbathnbr'].fillna(df_total['calculatedbathnbr'].median(), inplace=True)
df_total['calculatedfinishedsquarefeet'].fillna(df_total['calculatedfinishedsquarefeet'].median(), inplace=True)
df_total['fullbathcnt'].fillna(df_total['fullbathcnt'].median(), inplace=True)
df_total['heatingorsystemtypeid'].fillna(2, inplace=True) # mode
df_total['lotsizesquarefeet'].fillna(df_total['lotsizesquarefeet'].median(), inplace=True)
df_total['unitcnt'].fillna(df_total['unitcnt'].median(), inplace=True) # mode
df_total['yearbuilt'].fillna(df_total['yearbuilt'].median(), inplace=True)
df_total['numberofstories'].fillna(df_total['numberofstories'].median(), inplace=True)
df_total['structuretaxvaluedollarcnt'].fillna(df_total['structuretaxvaluedollarcnt'].median(), inplace=True)
df_total['taxvaluedollarcnt'].fillna(df_total['taxvaluedollarcnt'].median(), inplace=True)
df_total['landtaxvaluedollarcnt'].fillna(df_total['landtaxvaluedollarcnt'].median(), inplace=True)
df_total['taxamount'].fillna(df_total['taxamount'].median(), inplace=True)
df_total['taxdelinquencyflag'].fillna('N', inplace=True)


# There must be at least as many rooms as bedrooms plus bathrooms in the property. We are thus replacing the NaN with this sum.
df_total['roomcnt'].replace(0,np.nan, inplace=True)
df_total['roomcnt'].fillna(df_total['calculatedbathnbr'] + df_total['bedroomcnt'], inplace=True)


### Data Anomalies

# lotsizesquarefeet outliers all have value 3589145 or 6971010. We assume there is something irregular in the data entry.

def lot(a):
    if (a == 3589145 or a == 6971010):
        return df_total['lotsizesquarefeet'].median()
    else:
        return a

df_total['lotsizesquarefeet'] = df_total['lotsizesquarefeet'].map(lambda a: lot(a))


# The unitcnt outliers appear to reference the number of units in an entire complex whereas the property is a single unit.
def units(a):
    if (a > 20):
        return df_total['unitcnt'].median()
    else:
        return a

df_total['unitcnt'] = df_total['unitcnt'].map(lambda a: units(a))


# Several outliers have irregularities in most columns so we are removing them
df_total = df_total[df_total['calculatedfinishedsquarefeet'] >=100]

### Upload Output to AWS
output="data.csv"
zipname='data.zip'
df_total.to_csv(output, index=False)
z=zipfile.ZipFile(zipname,"w")
z.write(output)
z.close()

connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

bucket_name = 'zillowdata-esrkoutputdata'

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
