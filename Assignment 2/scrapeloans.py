import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
import configparser
import datetime

base1 = 'https://resources.lendingclub.com/LoanStats'

suffix1=['3a','3b','3c','3d','_2016Q1','_2016Q2','_2016Q3','_2016Q4','_2017Q1','_2017Q2','_2017Q3']



dataframe_collection = []

for suffix in suffix1:
  url = base1 + suffix + '.csv.zip'
  print(url)
  r = requests.get(url, stream=True)
  z = zipfile.ZipFile(BytesIO(r.content))
  df = pd.read_csv(z.open('LoanStats' + suffix + '.csv'),header=1,low_memory=False)
  dataframe_collection.append(df)

merged = pd.DataFrame(columns=dataframe_collection[0].columns.values.tolist())

for df in dataframe_collection:
  merged = merged.append(df)

merged['set']='accepted'
merged['timestamp']=datetime.datetime.now()

output='loanstats.csv'
merged.to_csv(output, index=False)


print("success")