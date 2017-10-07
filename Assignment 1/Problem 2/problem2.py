# # Processing the EDGAR Data Set: Missing Data Analysis

import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
from pandas import *
import re
import numpy
import scipy
from scipy import stats
import datetime
import matplotlib.pyplot as plt
import boto
import configparser
import logging


# Configure log file

logger = logging.getLogger('problem2')
hdlr = logging.FileHandler('problem2.log') # set the log file name
hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s')) # set the format for the log file
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) # enable info logging

# Input variables
config=configparser.RawConfigParser()
configFilePath=r'problem2.ini'
config.read(configFilePath)
year = config.get('problem-2', 'YEAR')
logger.info('year: ' + year)


AWS_ACCESS_KEY_ID = config.get('problem-2', 'AWS_ACCESS_KEY_ID')
logger.info('aws key id received')

AWS_SECRET_ACCESS_KEY = config.get('problem-2', 'AWS_SECRET_ACCESS_KEY')
logger.info('aws secret key received')

# ### Generate URLs


url_base = 'http://www.sec.gov/dera/data/Public-EDGAR-log-file-data/'
url_mid = '/log' + str(year)
url_final = '01.zip'
urls = []
# use range to get all 12 months
for x in range(1,13):
    if (x < 4):
        urls.append(url_base + str(year) + '/Qtr1' + url_mid + '0' + str(x) + url_final)
    elif (x >=4 and x < 7):
        urls.append(url_base + str(year) + '/Qtr2' + url_mid + '0' + str(x) + url_final)
    elif (x >= 7 and x < 10):
        urls.append(url_base + str(year) + '/Qtr3' + url_mid + '0' + str(x) + url_final)
    else:
        urls.append(url_base + str(year) + '/Qtr4' + url_mid + str(x) + url_final)

logger.info('Zip file URLs generated')


# The log files are large, so we will read them from the zip files instead of extracting them

column_names = ['ip','date','time','zone','cik','accession','doc/extention','code','filesize','idx','norefer','noagent','find','crawler','browser']

# Default Values:
# * ip: unknown
# * date: derive from file date
# * time: unknown
# * zone: 0
# * cik: unknown
# * accession: unknown
# * doc: unknown
# * code: unknown
# * size: mean
# * idx: 0
# * noreferer: 0
# * noagent: 0
# * find: 0
# * crawler: 0
# * browser: unknown
# 
# Numeric defaults are based on the README that comes with each log



dataframe_collection = []
for url in urls:
    logger.info('Reading csv from ' + url)
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(BytesIO(r.content))
    st = pd.read_csv(z.open(url[-15:-3]+'csv'))
    
    # Handle Missing Data
    logger.info('Handling missing data')
    # Replace missing numeric values and categorical that have default 0
    st.fillna({'zone': 0, 'idx': 0,'noreferer': 0,'noagent': 0,'find': 0,'crawler': 0}, inplace=True)
    # Replace missing categorical values
    st.fillna({'ip':'unknown', 'time':'unknown','cik':'unknown','accession':'unknown','code':'unknown','browser':'unknown'}, inplace=True)
    st.fillna({'doc':'unknown', 'extention':'unknown'}, inplace=True)
    # Replace missing dates from file name
    date_formatted = url[-12:-8]+'-'+url[-8:-6] + '-' + url[-6:-4]
    st.fillna({'date': date_formatted}, inplace=True)
    # Replace missing file sizes with mean
    st.fillna({'size': scipy.mean(st['size'])}, inplace=True)
    dataframe_collection.append(st)
    logger.info('Data frame added')


# Summary Data and Analyses

# ### Highest accession Number by month

def accessionNumber(df):
    allAccessionNumbers=[]
    Frequencies=[]
    modecount=df['accession'].value_counts()
    Frequencies.append(modecount[0])
    mode=df['accession'].value_counts().index.tolist()
    allAccessionNumbers.append(mode[0])
    dfAccessionNumber=pd.DataFrame({'Accession Number':allAccessionNumbers, 'Frequency':Frequencies})
    c=list(dfAccessionNumber.groupby('Accession Number')['Frequency'].sum())
    a=dfAccessionNumber.groupby('Accession Number')['Frequency'].sum().index.tolist()
    df1=pd.DataFrame({'Accession Number':a, 'Frequency':c})
    b=list(df1.loc[df1['Frequency']==df1.max()['Frequency']]['Accession Number'])
    mostFrequentAccessionNumber=pd.DataFrame({'Accession Number':[b[0]]})
    return mostFrequentAccessionNumber


logger.info('Identifying most common accession number by month')
accessionNumberPerMonth=[]
for i in range(0,len(dataframe_collection)):
    accessionNumberPerMonth.append(accessionNumber(dataframe_collection[i]))
months=['Jan','Feb','March','April','May','June','July','Aug','Sept','Oct','Nov','Dec']
accessionNumberPerMonth=pd.DataFrame({'Month': months,'Accession Number':accessionNumberPerMonth})
    


# ### Browser frequencies by month


def browserFrequency(df):
    modecount=df['browser'].value_counts()
    mode=modecount.index.tolist()
    dfBrowser=pd.DataFrame({'Browser':mode , 'Frequencies': modecount.values})
    return dfBrowser

logger.info('Identifying browser frequencies by month')
browserFrequencyByMonth=[]
for i in range(0,len(dataframe_collection)):
    browserf=browserFrequency(dataframe_collection[i])
    browserFrequencyByMonth.append(browserf)
    logger.info('Broswer frequencies added')


# ### Most Frequent times accessed

timeFrequencyCollection=[]
for x in range(0,len(dataframe_collection)):
    dftest=pd.DataFrame(dataframe_collection[x])
    dftest['time']=pd.to_datetime(dftest['time'])
    dftest.set_index(dftest['time'],inplace=True)
    dftest=dftest.groupby(TimeGrouper(freq='H'))
    d=dftest['time'].count()
    timeFrequencyCollection.append(d)
    timeFrequencyCollection[x]=pd.DataFrame(timeFrequencyCollection[x])

logger.info('Identifying time of day frequencies by month')
figTime, axTime = plt.subplots(nrows=6, ncols=2)
for i in range(0,len(timeFrequencyCollection)):
    plt.close('all')
    plt.subplot(6,2,i+1)
    axTime = timeFrequencyCollection[i]['time'].plot(kind='bar', title ="Most common time" + str(i),figsize=(15, 15), legend=True, fontsize=12)
    axTime.set_xlabel("Time", fontsize=12)
    axTime.set_ylabel("Frequency", fontsize=12)
    figTime = axTime.get_figure()
    figTime.savefig("TimeFrequencies" + str(i))
    #z.write("TimeFrequencies" + str(i) + ".png")
    logger.info('Time frequencies histogram saved')


# ### Top 5 CIK accessed in each file
logger.info('Identifying top 5 CIKs by month')
topFrequencyOfCIK=[]
for x in range(0,len(dataframe_collection)):
    c=list(dataframe_collection[x]['cik'].astype(int).astype(str))
    data=pd.DataFrame({'Cik':c})
    frequencyOfCik=data['Cik'].value_counts()
    freq=pd.DataFrame({'Frequency':frequencyOfCik})
    topFrequencyOfCIK.append(freq[:5])
    logger.info('Top 5 CIKs added')


# ### Outliers- Anomalies Observed in Size column

logger.info('Identifying file size outliers')

dfsize=[]
for x in range(0,len(dataframe_collection)):
    dfsize.append(dataframe_collection[x]['size'])
    dfsize[x]=pd.DataFrame(dfsize[x])

figSize, axSize = plt.subplots(nrows=6, ncols=2)
for i in range(0,len(dfsize)):
    plt.close('all')
    plt.subplot(6,2,i+1)
    axSize=dfsize[i]['size'].plot(kind='box',title ="Size outliers" + str(i),figsize=(15, 15), legend=True,fontsize=12,vert=False)
    figSize = axSize.get_figure()
    figSize.savefig("FileSizeOutliers" + str(i))
    #z.write("FileSizeOutliers" + str(i) + ".png")
    logger.info('File size box plot saved')


# Add data analysis to excel
writer=pd.ExcelWriter('logdata.xlsx',engine='xlsxwriter')

dfdes=[]

for x in range(0,len(dataframe_collection)):
    dfdes.append(dataframe_collection[x].describe())

for j in range(0,len(dfdes)):
    dfdes[j].to_excel(writer,sheet_name='Describe',startrow=(j*11))


accessionNumberPerMonth.to_excel(writer, sheet_name='Highest Accessed files by Month')


for x in range(0,len(browserFrequencyByMonth)):
    browserFrequencyByMonth[x].to_excel(writer,sheet_name='Browser Frequency By Month',startrow=0+x*14)
for i in range(0,len(topFrequencyOfCIK)):
    topFrequencyOfCIK[i].to_excel(writer,sheet_name='Top 5 CIK',startrow=0+i*7)

# Write all log data to excel
for y in range(0, len(dataframe_collection)):
    dataframe_collection[y].to_excel(writer,sheet_name='Month ' + str(y))


writer.save()
logger.info('Data saved to logdata.xlsx')

# Create output zip file
zipname = "edgarlogs" + str(year) + ".zip"
z = zipfile.ZipFile(zipname, "w")
logger.info('Zip file created: ' + zipname)


# Add log file and output files to zip
z.write('TimeFrequencies0.png')
z.write('TimeFrequencies1.png')
z.write('TimeFrequencies2.png')
z.write('TimeFrequencies3.png')
z.write('TimeFrequencies4.png')
z.write('TimeFrequencies5.png')
z.write('TimeFrequencies6.png')
z.write('TimeFrequencies7.png')
z.write('TimeFrequencies8.png')
z.write('TimeFrequencies9.png')
z.write('TimeFrequencies10.png')
z.write('TimeFrequencies11.png')
z.write('FileSizeOutliers0.png')
z.write('FileSizeOutliers1.png')
z.write('FileSizeOutliers2.png')
z.write('FileSizeOutliers3.png')
z.write('FileSizeOutliers4.png')
z.write('FileSizeOutliers5.png')
z.write('FileSizeOutliers6.png')
z.write('FileSizeOutliers7.png')
z.write('FileSizeOutliers8.png')
z.write('FileSizeOutliers9.png')
z.write('FileSizeOutliers10.png')
z.write('FileSizeOutliers11.png')
z.write('problem2.log')
z.write('logdata.xlsx')
z.close()


# Post zip file to AWS S3

connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

bucket_name = AWS_ACCESS_KEY_ID.lower() + '-outputproblem2'

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

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


s3key = boto.s3.key.Key(bucket)
s3key.key = zipname
s3key.set_contents_from_filename(zipname, cb=percent_cb, num_cb=10)
print("success")

