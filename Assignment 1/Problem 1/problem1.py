#!/usr/local/bin/python3

# Working with Edgar datasets: Wrangling, Pre-processing and exploratory data analysis

from lxml import html
from lxml.html import parse
import requests
import html5lib
import pandas as pd
from pandas.io.parsers import TextParser
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import sys


# Input variables (need to set as environmental variables for Docker pipline)

cik = '51143'
acc_no = '0000051143-13-000007'
acc_short = acc_no[0:10] + acc_no[11:13] + acc_no[14:]


# Generate full URL and get the page

page = requests.get('https://www.sec.gov/Archives/edgar/data/' + cik + '/' + acc_short + '/' + acc_no +'-index.htm')
source = page.content


# Scrape page content for links, find 10Q

htmlcontent = html.document_fromstring(source)

href = ''
for elem in htmlcontent.iterlinks():
    if "10q.htm" in elem[2]:
        href+= elem[2]

url10q = 'https://www.sec.gov' + href

# Scrape Tables with BeautifulSoup

soup = BeautifulSoup(requests.get(url10q).text, 'lxml')
csvout  = csv.writer(sys.stdout)

tables=soup.findAll('table')

# Iterate through tables and generate csvs
table_count=0

for table in tables:
    rows = table.findAll('tr')
    clean_table = [] 
    
    for row in rows:
        clean_row = []
        columns = row.find_all('td')
        for column in columns:
            clean_row.append(column.get_text().replace("\n","").replace("\xa0",""))
        clean_table.append(clean_row)
        #print(clean_row)
    frame = pd.DataFrame(clean_table)
    #print(frame)
    csv_name = acc_no + "_" + str(table_count) + ".csv"
    frame.to_csv(csv_name)
    table_count +=1

