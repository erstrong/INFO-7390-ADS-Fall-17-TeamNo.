import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
import configparser
import datetime


base2 = 'https://resources.lendingclub.com/RejectStats'

suffix2=['A','B','D','_2016Q1','_2016Q2','_2016Q3','_2016Q4','_2017Q1','_2017Q2','_2017Q3']

dataframe_collection2 = []

for suffix in suffix2:
    url = base2 + suffix + '.csv.zip'
    print(url)
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(BytesIO(r.content))
    df = pd.read_csv(z.open('RejectStats' + suffix + '.csv'),header=1,low_memory=False)
    dataframe_collection2.append(df)

merged2 = pd.DataFrame(columns=dataframe_collection2[0].columns.values.tolist())
for df in dataframe_collection2:
    merged2 = merged2.append(df)

merged2['set'] ='declined'
merged2['timestamp']=datetime.datetime.now()
output2='declinestats.csv'
merged2.to_csv(output2, index=False)



print("success")