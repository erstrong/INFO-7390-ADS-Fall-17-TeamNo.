# # Part 1 - Data Ingestion, EDA, Wrangling
# 
# The data:
# 
# * properties_2017.csv is a sample of all properties from 2017 listed on Zillow through Sept
# * train_2017.csv contains dates, propertyids, and logerror for each transaction in 2017 through Sept
# * The same files are available for 2016 (entire year)
# * Not all properties have transactions
# * logerror=log(Zestimate)−log(SalePrice)
# 



import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

### Data Format Cleanup

#### Years
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

df_merged['taxdelinquencyyear'] = df_merged['taxdelinquencyyear'].map(lambda a: convertyears(a))

#### Latitude and Longitude
# The values are missing decimal points. Transform each column by dividing by 1000000.
# Also drop all NAs since we will need to use accurate coordinates in Part 4 and thus should not
# fill missing values.


df_merged16 = df_merged.dropna(subset=['latitude'])
df_merged16 = df_merged.dropna(subset=['longitude'])
df_merged17 = df_merged.dropna(subset=['latitude'])
df_merged17 = df_merged.dropna(subset=['longitude'])

df_merged16['latitude'] = df_merged16['latitude'] / 1000000
df_merged16['longitude'] = df_merged16['longitude'] / 1000000
df_merged17['latitude'] = df_merged17['latitude'] / 1000000
df_merged17['longitude'] = df_merged17['longitude'] / 1000000




#df_merged.reset_index()

### Check NAs and Data Types
#df_merged.dtypes
#df_merged.isnull().any()

# Almost all columns have NAs, so look at how many data points each column has
#df_merged.count()

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
df_merged.drop('pooltypeid10', axis=1, inplace=True)
df_merged.drop('pooltypeid2', axis=1, inplace=True)
df_merged.drop('pooltypeid7', axis=1, inplace=True)
df_merged.drop('storytypeid', axis=1, inplace=True)
df_merged.drop('typeconstructiontypeid', axis=1, inplace=True)
df_merged.drop('yardbuildingsqft17', axis=1, inplace=True)
df_merged.drop('yardbuildingsqft26', axis=1, inplace=True)
df_merged.drop('threequarterbathnbr', axis=1, inplace=True)
df_merged.drop('hashottuborspa', axis=1, inplace=True)



# #### Missing Values

## These numbers are actually categorical, use mode -- or should we use 5:"None"?
df_merged['airconditioningtypeid'].fillna(5, inplace=True)


# In[ ]:


df_merged['bathroomcnt'].describe()


# In[38]:


# bathroomcnt and calculatedbathnbr have the same definition in data dictionary
# The data is identical between the two columns, except that calculatedbathnbr has NaN
# where bathroomcnt has zero. We will keep calculatedbathnbr and replace the NaN with
# the median since it is unlikely the residences have zero bathrooms.
# Data is skewed so use median
df_merged['calculatedbathnbr'].fillna(df_merged['calculatedbathnbr'].median(), inplace=True)
df_merged.drop('bathroomcnt', axis=1, inplace=True)


# Data is skewed so use median
#df_merged['bedroomcnt'].fillna(df_merged['bedroomcnt'].median(), inplace=True)
# There is no missing data in this column


df_merged['buildingqualitytypeid'].fillna(df_merged['buildingqualitytypeid'].mean(), inplace=True)


# Data is skewed so use median
df_merged['calculatedfinishedsquarefeet'].fillna(df_merged['calculatedfinishedsquarefeet'].median(), inplace=True)



# finishedsquarefeet12 has the same definited as calculatedfinishedsquarefeet in the data dictionary
# and more missing values, so we are dropping it
df_merged.drop('finishedsquarefeet12', axis=1, inplace=True)


# fireplacecnt is at the threshold for the missing data cutoff but since there are no 0s, we can
# reasonably assume that missing values are 0s.

df_merged['fireplacecnt'].fillna(0, inplace=True)

# We can calculate the missing valeus for fireplaceflag from fireplacecnt
# Currently where there is a value it is "true", we will change this
df_merged['fireplaceflag'] = False
df_merged.loc[df_merged['fireplacecnt'] > 0, 'fireplaceflag'] = True


df_merged['fullbathcnt'].fillna(df_merged['fullbathcnt'].median(), inplace=True)


df_merged['garagecarcnt'].fillna(0, inplace=True)


df_merged['garagetotalsqft'].replace(0,np.nan, inplace=True)

df_merged.groupby('garagecarcnt')['garagetotalsqft'].describe()


# In[81]:


df_merged.loc[df_merged['garagecarcnt']>0, 'garagetotalsqft'].fillna(df_merged['garagetotalsqft'].mean(), inplace=True)


# In[82]:


df_merged.groupby('garagecarcnt')['garagetotalsqft'].describe()


# In[77]:


df_merged['garagetotalsqft'].fillna(0, inplace=True)


# In[78]:


df_merged.groupby('garagecarcnt')['garagetotalsqft'].describe()


# In[126]:


plt.scatter(df_merged['garagetotalsqft'],df_merged['logerror'])
plt.show()


# In[114]:


## TODO the above isn't working


# In[116]:


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

df_merged['taxdelinquencyyear'] = df_merged['taxdelinquencyyear'].map(lambda a: convertyears(a))



df_merged['heatingorsystemtypeid'].fillna(df_merged['heatingorsystemtypeid'].mode(), inplace=True)

df_merged['lotsizesquarefeet'].fillna(df_merged['lotsizesquarefeet'].median(), inplace=True)

df_merged['poolcnt'].fillna(0, inplace=True)

df_merged['roomcnt'].replace(0,np.nan, inplace=True)


# There must be at least as many rooms as bedrooms plus bathrooms in the property. We are thus replacing the NaN with this sum.


df_merged['roomcnt'].fillna(df_merged['calculatedbathnbr'] + df_merged['bedroomcnt'], inplace=True)

df_merged['unitcnt'].fillna(df_merged['unitcnt'].mode(), inplace=True)

df_merged['yearbuilt'].fillna(df_merged['yearbuilt'].median(), inplace=True)

df_merged['numberofstories'].fillna(df_merged['numberofstories'].median(), inplace=True)

df_merged['structuretaxvaluedollarcnt'].fillna(df_merged['structuretaxvaluedollarcnt'].median(), inplace=True)

df_merged['taxvaluedollarcnt'].fillna(df_merged['taxvaluedollarcnt'].median(), inplace=True)

df_merged['landtaxvaluedollarcnt'].fillna(df_merged['landtaxvaluedollarcnt'].median(), inplace=True)

df_merged['taxamount'].fillna(df_merged['taxamount'].median(), inplace=True)

df_merged['taxdelinquencyflag'].fillna('N', inplace=True)


# Rawcensustractandblock and censustractandblock are the same according to the data dictionary. 
df_merged['rawcensustractandblock'].describe()
df_merged['censustractandblock'].max()
df_merged['censustractandblock'].min()
df_merged['rawcensustractandblock'].max()
df_merged['rawcensustractandblock'].min()


# The raw value has the format FIPS + tract information with no missing values.
# Dropping censustractandblock, which appears to have anomolies as well as missing data.

df_merged.drop('censustractandblock', axis=1, inplace=True)


