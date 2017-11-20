import zipfile
import requests
from io import StringIO,BytesIO
import pandas as pd
import configparser
import datetime
from bs4 import BeautifulSoup
import numpy as np
from sklearn.externals import joblib
from sklearn import cluster
import pickle
import luigi
import os

class scrapeDeclineData(luigi.Task):
	
	def run(self):
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

		declined = pd.DataFrame(columns=dataframe_collection2[0].columns.values.tolist())
		for df2 in dataframe_collection2:
			declined = declined.append(df2)

## Data Cleansing

# Convert Application Date to Datetime
		format = '%Y-%m-%d'
		declined['Application Date'] = declined['Application Date'].map(lambda a: datetime.datetime.strptime(a, format))

# Convert Vantage scores to same scale as FICO
		m1=(declined['Application Date'] >='2013-11-06')
		declined.loc[m1,'Risk_Score']=declined.loc[m1,'Risk_Score'] * (85/99)

# Replace impossible credit scores and fill NAs
		m2=(declined['Risk_Score'] <350)
		declined.loc[m2,'Risk_Score']=declined['Risk_Score'].mean()

		declined['Risk_Score'].fillna(declined['Risk_Score'].mean(), inplace=True)
		declined['Loan Title'].fillna('None', inplace=True)
		declined['Policy Code'].fillna(0, inplace=True)

# Drop rows missing location data
		declined.dropna(subset=['Zip Code'], inplace=True)
		declined.dropna(subset=['State'], inplace=True)

# Drop Application Date since Loan Stats doesn't have this
		declined.drop('Application Date', axis=1, inplace=True)

# Reformat Debt-To-Income data
		declined['Debt-To-Income Ratio'] = declined['Debt-To-Income Ratio'].map(lambda a: float(a.strip('%')))
		declined=declined[declined['Debt-To-Income Ratio'] >=0]

# Reformat employment length
		def elength(a):
			if (a=='n/a'):
				return 0
			elif (a=='10+ years'):
				return 10
			elif (a=='1 year'):
				return 1
			elif (a=='< 1 year'):
				return 0.5
			else:
				return float(a.strip(' years'))

		declined['Employment Length'] = declined['Employment Length'].map(lambda a: elength(a))


# Rename columns to match equivalent Loan Stats column
		declined=declined.rename(columns = {'Amount Requested':'loan_amnt','Loan Title':'title','Risk_Score':'fico_range_low','Debt-To-Income Ratio':'dti','Zip Code':'zip_code','State':'addr_state','Employment Length':'emp_length','Policy Code':'policy_code'})

		declined['set'] ='declined'
		declined.to_csv(self.output().path,index=False)

	def output(self):
		return luigi.LocalTarget("CleanDeclined.csv")

class AggregateData(luigi.Task):
	def requires(self):
		#yield scrapeLoanData()
		yield scrapeDeclineData()
	
	def run(self):
		#loans=pd.read_csv(scrapeLoanData.output())
		declined=pd.read_csv(scrapeDeclineData().output().path, encoding = "ISO-8859-1")
		columns=['loan_amnt','fico_range_low','dti','emp_length','policy_code','set']

		#merged=loans[columns]
		#merged=declined[columns]
		#merged = merged.append(declined[columns])
		
	
		declinedData=pd.DataFrame()
		declinedData=declined[columns]
		declinedData.to_csv(self.output().path,index=False)

	def output(self):
		return luigi.LocalTarget('declinedData.csv')
	

if __name__=='__main__':
	luigi.run()