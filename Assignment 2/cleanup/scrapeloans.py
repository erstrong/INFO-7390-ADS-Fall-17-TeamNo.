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
dataframe_collection = []


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
    r = session.get(base1 + suf, params = parameters, stream=True)
    #print(r.status_code)
    z = zipfile.ZipFile(BytesIO(session.get(base1 + suf, params=parameters, stream=True).content))
    df = pd.read_csv(z.open(zip[:-4]),header=1,low_memory=False)
    #df.to_csv(zip[:-4], index=False)
    dataframe_collection.append(df)


loans = pd.DataFrame(columns=dataframe_collection[0].columns.values.tolist())

for df in dataframe_collection:
    loans = loans.append(df)

loans['set']='accepted'
loans['timestamp']=datetime.datetime.now()


## Data Cleansing

# Columns with > 50% missing data:
missing_percents = (len(loans.index) - loans.count())/len(loans.index)
drops = missing_percents[missing_percents > .5]
columns = drops.index
for c in columns:
    loans.drop(c, axis=1, inplace=True)

# Columns with data related to loan processing after application
# We are keeping the grade and sub_grade in our raw data file to use for evaluating clusters
drops2=['installment','url','issue_d','funded_amnt','funded_amnt_inv','verification_status','loan_status','pymnt_plan','initial_list_status','out_prncp','out_prncp_inv','total_pymnt','total_pymnt_inv','total_rec_int','total_rec_late_fee','total_rec_prncp','recoveries','collection_recovery_fee','last_pymnt_d','last_pymnt_amnt','hardship_flag','disbursement_method','debt_settlement_flag','last_credit_pull_d','last_fico_range_high','last_fico_range_low','next_pymnt_d']

for d in drops2:
    loans.drop(d, axis=1, inplace=True)

# Redundant columns
drops3=['pub_rec','acc_now_delinq','tot_coll_amt','delinq_amnt','num_bc_sats','num_tl_120dpd_2m','pct_tl_nvr_dlq','inq_last_6mths','acc_open_past_24mths','mo_sin_old_rev_tl_op','mo_sin_rcnt_rev_tl_op','earliest_cr_line','total_rev_hi_lim','avg_cur_bal','bc_open_to_buy','tot_hi_cred_lim','total_bal_ex_mort','total_il_high_credit_limit','num_op_rev_tl','fico_range_high']

for d in drops3:
    loans.drop(d, axis=1, inplace=True)

# Not useful for analysis
drops4 = ['title','emp_title','zip_code','purpose']
          
for d in drops4:
    loans.drop(d, axis=1, inplace=True)


loans = loans[np.isfinite(loans['loan_amnt'])]

# Mean, median, and mode substitutions
#loans["emp_title"].fillna("Not provided", inplace=True)
loans["annual_inc"].fillna(loans["annual_inc"].mean(), inplace=True)
#loans["title"].fillna("Debt consolidation",inplace=True) # mode
loans["mths_since_last_delinq"].fillna(loans['mths_since_last_delinq'].max(),inplace=True)
loans["mths_since_recent_inq"].fillna(loans["mths_since_recent_inq"].median(),inplace=True)

def inc(a):
    if a > 100000000:
        return loans['annual_inc'].mean()
    else:
        return a
loans['annual_inc'] = loans['annual_inc'].map(lambda a: inc(a))


# For remaining columns, the number of missing values are very small relative to the size of the data set so we are dropping the rows with missing values
#loans.dropna(subset=['zip_code'], inplace=True)
loans.dropna(subset=['dti'], inplace=True)
loans.dropna(subset=['delinq_2yrs'], inplace=True)
loans.dropna(subset=['open_acc'], inplace=True)
loans.dropna(subset=['revol_util'], inplace=True)
loans.dropna(subset=['total_acc'], inplace=True)
loans.dropna(subset=['last_credit_pull_d'], inplace=True)
loans.dropna(subset=['collections_12_mths_ex_med'], inplace=True)
loans.dropna(subset=['chargeoff_within_12_mths'], inplace=True)
loans.dropna(subset=['pub_rec_bankruptcies'], inplace=True)
loans.dropna(subset=['tax_liens'], inplace=True)
loans.dropna(subset=['tot_cur_bal'], inplace=True)
loans.dropna(subset=['bc_util'], inplace=True)
loans.dropna(subset=['mo_sin_old_il_acct'], inplace=True)
loans.dropna(subset=['mths_since_recent_bc'], inplace=True)
loans.dropna(subset=['num_rev_accts'], inplace=True)
loans.dropna(subset=['percent_bc_gt_75'], inplace=True)
loans.dropna(subset=['mo_sin_old_il_acct'], inplace=True)

# Remove rows with DTI < 0
loans=loans[loans['dti'] >=0]

# Convert formats
loans['int_rate'] = loans['int_rate'].map(lambda a: float(a.strip('%')))

loans['term'] = loans['term'].map(lambda a: int(a.strip(' months')))
loans['application_type'] = loans['application_type'].map(lambda a: 1 if a=='Joint App' else 0)

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

loans['emp_length'] = loans['emp_length'].map(lambda a: elength(a))

loans['revol_util'] = loans['revol_util'].map(lambda a: float(a.strip('%')))

homes = pd.get_dummies(loans['home_ownership'], prefix='home')
loans = loans.join(homes)
loans.drop('home_ownership', axis=1, inplace=True)

homes = pd.get_dummies(loans['addr_state'], prefix='home')
loans = loans.join(homes)
loans.drop('addr_state', axis=1, inplace=True)

output='loanstats.csv'
loans.to_csv(output, index=False)

print("success")