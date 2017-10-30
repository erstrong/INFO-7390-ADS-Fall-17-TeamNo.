import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from uszipcode import ZipcodeSearchEngine


### Read Environmental Variables
AWS_ACCESS_KEY_ID = sys.argv[1]
AWS_SECRET_ACCESS_KEY = sys.argv[2]

### Data Ingestion

# First import the properties files
df16 = pd.read_csv('properties_2016.csv', low_memory=False)
df17 = pd.read_csv('properties_2017.csv', low_memory=False)

# Then import the transaction data
df_transactions17 = pd.read_csv('train_2016_v2.csv', low_memory=False)
df_transactions17 = pd.read_csv('train_2017.csv', low_memory=False)

# Next match the properties to transactions on ParcelID, using a right join
df_merged16 = pd.merge(df16, df_transactions16, on='parcelid', how='right')
df_merged17 = pd.merge(df17, df_transactions17, on='parcelid', how='right')

#### Latitude and Longitude
# Drop all NAs since we will need to use accurate coordinates in Part 4 and thus should not
# fill missing values.

df_merged16 = df_merged.dropna(subset=['latitude'])
df_merged16 = df_merged.dropna(subset=['longitude'])
df_merged17 = df_merged.dropna(subset=['latitude'])
df_merged17 = df_merged.dropna(subset=['longitude'])



# Combine the two data sets
df_merged16['setyear'] = 2016
df_merged17['setyear'] = 2017
df_total_t1 = df_merged16.append(df_merged17, ignore_index=True)

### Data Format Cleanup

#### Latitude and longitude
# The values are missing decimal points. Transform each column by dividing by 1000000.
df_total_t1['latitude'] = df_total_t1['latitude'] / 1000000
df_total_t1['longitude'] = df_total_t1['longitude'] / 1000000


#### Tax Delinquency Years
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

df_total_t1['taxdelinquencyyear'] = df_total_t1['taxdelinquencyyear'].map(lambda a: convertyears(a))

#### Transaction Date
format = '%Y-%m-%d'
df_total_t1['transactiondate'] = df_total_t1['transactiondate'].map(lambda a: datetime.datetime.strptime(a, format))


#### Pool Types Column
df_total_t1['poolcnt'].fillna(0, inplace=True)
df_total_t1['hashottuborspa'].fillna(False, inplace=True)
pools = pd.DataFrame(columns=['parcelid','pooltype'])
for i, row in df_total_t1.iterrows():
    if row['hashottuborspa'] and row['poolcnt'] > 0:
        pools.loc[len(pools)] = [row['parcelid'],2]
    elif not(row['hashottuborspa']) and row['poolcnt'] > 0:
        pools.loc[len(pools)] = [row['parcelid'],7]
    elif row['hashottuborspa'] and row['poolcnt'] == 0:
        pools.loc[len(pools)] = [row['parcelid'],10]
    else:
        pools.loc[len(pools)] = [row['parcelid'],0]
df_total_t2 = pd.merge(df_total_t1, pools, on='parcelid', how='left')

#### Zip Codes
search = ZipcodeSearchEngine()
for i, row in df_total_t2.iterrows():
    b = search.by_coordinate(row['latitude'],row['longitude'])
    zips.loc[len(zips)] = [row['parcelid'],b[0].Zipcode]
df_total = pd.merge(df_total_t2, zips, on='parcelid', how='left')

df_total.reset_index()

### Remove data we will not be using based on the EDA

# A few of the columns with >80% missing data we will examine more closely to determine if they
# can be calculated, but for the rest we are dropping them


df_merged.drop('architecturalstyletypeid', axis=1, inplace=True)
df_merged.drop('basementsqft', axis=1, inplace=True)
df_merged.drop('buildingclasstypeid', axis=1, inplace=True)
df_merged.drop('decktypeid', axis=1, inplace=True)
df_merged.drop('finishedfloor1squarefeet', axis=1, inplace=True)
df_merged.drop('finishedsquarefeet13', axis=1, inplace=True)
df_merged.drop('finishedsquarefeet15', axis=1, inplace=True)
df_merged.drop('finishedsquarefeet50', axis=1, inplace=True)
df_merged.drop('finishedsquarefeet6', axis=1, inplace=True)
df_merged.drop('poolsizesum', axis=1, inplace=True)
df_merged.drop('storytypeid', axis=1, inplace=True)
df_merged.drop('typeconstructiontypeid', axis=1, inplace=True)
df_merged.drop('yardbuildingsqft17', axis=1, inplace=True)
df_merged.drop('yardbuildingsqft26', axis=1, inplace=True)
df_merged.drop('threequarterbathnbr', axis=1, inplace=True)
df_merged.drop('censustractandblock', axis=1, inplace=True)
df_merged.drop('bathroomcnt', axis=1, inplace=True)
df_merged.drop('finishedsquarefeet12', axis=1, inplace=True)


#### Missing Values

# For AC Type use "None"
df_merged['airconditioningtypeid'].fillna(5, inplace=True)

# bathroomcnt and calculatedbathnbr have the same definition in data dictionary
# The data is identical between the two columns, except that calculatedbathnbr has NaN
# where bathroomcnt has zero. We will keep calculatedbathnbr and replace the NaN with
# the median since it is unlikely the residences have zero bathrooms.
# Data is skewed so use median
df_merged['calculatedbathnbr'].fillna(df_merged['calculatedbathnbr'].median(), inplace=True)



# finishedsquarefeet12 has the same definited as calculatedfinishedsquarefeet in the data dictionary
# and more missing values, so we are dropping it



# fireplacecnt is at the threshold for the missing data cutoff but since there are no 0s, we can
# reasonably assume that missing values are 0s.

df_merged['fireplacecnt'].fillna(0, inplace=True)

# Calculate the missing valeus for fireplaceflag from fireplacecnt
# Currently where there is a value it is "true", we will change this
df_merged['fireplaceflag'] = False
df_merged.loc[df_merged['fireplacecnt'] > 0, 'fireplaceflag'] = True



#### TODO FIX GARAGES

#df_merged['garagecarcnt'].fillna(0, inplace=True)
#df_merged['garagetotalsqft'].replace(0,np.nan, inplace=True)
#df_merged.loc[df_merged['garagecarcnt']>0, 'garagetotalsqft'].fillna(df_merged['garagetotalsqft'].mean(), inplace=True)
#df_merged['garagetotalsqft'].fillna(0, inplace=True)




# There must be at least as many rooms as bedrooms plus bathrooms in the property. We are thus replacing the NaN with this sum.
df_merged['roomcnt'].replace(0,np.nan, inplace=True)
df_merged['roomcnt'].fillna(df_merged['calculatedbathnbr'] + df_merged['bedroomcnt'], inplace=True)


# Median and Mode Replacements
# Data is skewed so use median rather than mean for anything that is a count

#df_merged['bedroomcnt'].fillna(df_merged['bedroomcnt'].median(), inplace=True)
# There is no missing data in this column


df_merged['buildingqualitytypeid'].fillna(df_merged['buildingqualitytypeid'].mean(), inplace=True)
df_merged['calculatedfinishedsquarefeet'].fillna(df_merged['calculatedfinishedsquarefeet'].median(), inplace=True)
df_merged['fullbathcnt'].fillna(df_merged['fullbathcnt'].median(), inplace=True)
df_merged['heatingorsystemtypeid'].fillna(df_merged['heatingorsystemtypeid'].mode(), inplace=True)
df_merged['lotsizesquarefeet'].fillna(df_merged['lotsizesquarefeet'].median(), inplace=True)
df_merged['unitcnt'].fillna(df_merged['unitcnt'].mode(), inplace=True)
df_merged['yearbuilt'].fillna(df_merged['yearbuilt'].median(), inplace=True)
df_merged['numberofstories'].fillna(df_merged['numberofstories'].median(), inplace=True)
df_merged['structuretaxvaluedollarcnt'].fillna(df_merged['structuretaxvaluedollarcnt'].median(), inplace=True)
df_merged['taxvaluedollarcnt'].fillna(df_merged['taxvaluedollarcnt'].median(), inplace=True)
df_merged['landtaxvaluedollarcnt'].fillna(df_merged['landtaxvaluedollarcnt'].median(), inplace=True)
df_merged['taxamount'].fillna(df_merged['taxamount'].median(), inplace=True)
df_merged['taxdelinquencyflag'].fillna('N', inplace=True)


### Upload Output to AWS


