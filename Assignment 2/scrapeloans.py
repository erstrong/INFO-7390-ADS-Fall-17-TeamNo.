import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
import configparser
import datetime
from bs4 import BeautifulSoup


# Get the list of files to read
login = 'https://www.lendingclub.com/account/login.action'
values= {'login_email':'','login_password':''}
page='https://www.lendingclub.com/info/download-data.action'

suffix=[]
base1 = 'https://resources.lendingclub.com/'
#dataframe_collection = []


session = requests.Session()
session.post(login, data=values)
soup=BeautifulSoup(session.get(page).text, 'lxml')
div=soup.find('div',id='loanStatsFileNamesJS')
div = str(div)
#print(div)
t = div.split(">")
t1=t[1].split("<")
t2 = t1[0].split("|")
suffix = t2[0:len(t2)-1]
for suf in suffix:
    print(suf)
    url = base1 + suf.split('?')[0]
    zip=suf.split('?')[0]
    zip=zip.split('/')[1]
    p = suf.split('?')[1]
    p = p.split('&amp;')
    sig = p[0].split('=')[1]
    iss = p[1].split('=')[1]
    parameters = {'signature':sig, 'issued':iss}
    #s.post(login, data=values)
    r = session.get(base1 + suf, params = parameters, stream=True)
    #print(r.status_code)
    z = zipfile.ZipFile(BytesIO(session.get(base1 + suf, params=parameters, stream=True).content))
    df = pd.read_csv(z.open(zip[:-4]),header=1,low_memory=False)
    df.to_csv(zip[:-4], index=False)
#dataframe_collection.append(df)

#suffix1=['3a','3b','3c','3d','_2016Q1','_2016Q2','_2016Q3','_2016Q4','_2017Q1','_2017Q2','_2017Q3']


print("success")