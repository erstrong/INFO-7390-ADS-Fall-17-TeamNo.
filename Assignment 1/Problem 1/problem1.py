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
import logging
import zipfile
import boto

# Configure log file

logger = logging.getLogger('problem1')
hdlr = logging.FileHandler('problem1.log') # set the log file name
hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s')) # set the format for the log file
logger.addHandler(hdlr)
logger.setLevel(logging.INFO) # enable info logging

# Input variables
cik = sys.argv[1]
logger.info('cik: ' + cik)

acc_no = sys.argv[2]
logger.info('acc_no: ' + acc_no)
acc_short = acc_no[0:10] + acc_no[11:13] + acc_no[14:]
logger.info('acc_short generated')

AWS_ACCESS_KEY_ID = sys.argv[3]
logger.info('aws key id received')

AWS_SECRET_ACCESS_KEY = sys.argv[4]
logger.info('aws secret key received')

#print(sys.argv)


# Generate full URL and get the page


page = 'https://www.sec.gov/Archives/edgar/data/' + cik + '/' + acc_short + '/' + acc_no +'-index.htm'

try:
    dfs = pd.read_html(page, header=0)
except urllib.error.HTTPError:
    print("CIK or accession number is invalid")
except:
    print("Unexpected error:", sys.exc_info()[0])

documents = dfs[0]
logger.info('Documents table scraped')

row10q= documents.loc[documents['Type'] == '10-Q']
url10q='https://www.sec.gov/Archives/edgar/data/' + cik + '/' + acc_short + '/' + str(row10q['Document'][0])
logger.info('10-Q url generated: ' + url10q)

# Scrape Tables with BeautifulSoup

soup = BeautifulSoup(requests.get(url10q).text, 'lxml')
logger.info('10-Q page accessed')

tables=soup.findAll('table')
logger.info('tables scraped')

# Iterate through tables and generate csvs
table_count=0
zipname = "10QTables_" + acc_no + ".zip"
z = zipfile.ZipFile(zipname, "w")

for table in tables:
    logger.info('cleaning table...')
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
    # logger.info(csv_name + ' created')
    z.write(csv_name)
    logger.info(csv_name + ' added to zip file')
    table_count +=1

# Zip log file with the csvs

z.write('problem1.log')
z.close()

# Post zip file to AWS S3

connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

bucket_name = AWS_ACCESS_KEY_ID.lower() + '-output'

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
