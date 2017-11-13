import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
import configparser
import datetime
from bs4 import BeautifulSoup

# Get the list of files to read
page='https://www.lendingclub.com/info/download-data.action'

soup = BeautifulSoup(requests.get(page).text, 'lxml')



div =soup.find('div',id='loanStatsFileNamesJS')
div = str(div)
t = div.split(">")
t1=t[1].split("<")
t2 = t1[0].split("|")
suffix1 = t2[0:len(t2)-1]
#suffix1=['3a','3b','3c','3d','_2016Q1','_2016Q2','_2016Q3','_2016Q4','_2017Q1','_2017Q2','_2017Q3']

base1 = 'https://resources.lendingclub.com/'

# Iterate through the list and read the csv into a data frame
dataframe_collection = []

for suffix in suffix1:
  url = base1 + suffix
  print(url)
  r = requests.get(url, stream=True)
  z = zipfile.ZipFile(BytesIO(r.content))
  df = pd.read_csv(z.open(suffix[:-4]),header=1,low_memory=False)
  dataframe_collection.append(df)

merged = pd.DataFrame(columns=dataframe_collection[0].columns.values.tolist())

for df in dataframe_collection:
  merged = merged.append(df)

merged['set']='accepted'
merged['timestamp']=datetime.datetime.now()

output='loanstats.csv'
merged.to_csv(output, index=False)


print("success")