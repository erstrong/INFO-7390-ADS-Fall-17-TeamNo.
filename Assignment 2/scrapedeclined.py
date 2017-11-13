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

div =soup.find('div',id='rejectedLoanStatsFileNamesJS')
div = str(div)
t = div.split(">")
t1=t[1].split("<")
t2 = t1[0].split("|")
suffix2 = t2[0:len(t2)-1]


base = 'https://resources.lendingclub.com/'

#suffix2=['A','B','D','_2016Q1','_2016Q2','_2016Q3','_2016Q4','_2017Q1','_2017Q2','_2017Q3']

# Iterate through the list and read the csv into a data frame
dataframe_collection2 = []

for suffix in suffix2:
    url = base + suffix
    print(url)
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(BytesIO(r.content))
    df = pd.read_csv(z.open(suffix[:-4]),header=1,low_memory=False)
    dataframe_collection2.append(df)

merged2 = pd.DataFrame(columns=dataframe_collection2[0].columns.values.tolist())
for df in dataframe_collection2:
    merged2 = merged2.append(df)

merged2['set'] ='declined'
merged2['timestamp']=datetime.datetime.now()
output2='declinestats.csv'
merged2.to_csv(output2, index=False)



print("success")