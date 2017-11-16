import pandas as pd
import numpy as np
import datetime

pd.set_option('float_format', '{:f}'.format)

filelist=['LoanStats3a_securev1.csv','LoanStats3b_securev1.csv','LoanStats3c_securev1.csv','LoanStats3d_securev1.csv','LoanStats_securev1_2016Q1.csv','LoanStats_securev1_2016Q2.csv','LoanStats_securev1_2016Q3.csv','LoanStats_securev1_2016Q4.csv','LoanStats_securev1_2017Q1.csv','LoanStats_securev1_2017Q2.csv','LoanStats_securev1_2017Q3.csv']

dataframe_collection = []

for file in filelist:
    df = pd.read_csv(file, low_memory=False)
    dataframe_collection.append(df)

# Iterate through the list and read the csv into a data frame
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

# Columns with data related to loan activities
drops2=['url','funded_amnt','funded_amnt_inv','verification_status','loan_status','pymnt_plan','initial_list_status','out_prncp','out_prncp_inv','total_pymnt','total_pymnt_inv','total_rec_int','total_rec_late_fee','total_rec_prncp','recoveries','collection_recovery_fee','last_pymnt_d','last_pymnt_amnt','hardship_flag','disbursement_method','debt_settlement_flag']

for d in drops2:
    loans.drop(d, axis=1, inplace=True)

# Redundant columns
drops3=['pub_rec','acc_now_delinq','tot_coll_amt','delinq_amnt','num_bc_sats','num_tl_120dpd_2m','pct_tl_nvr_dlq','inq_last_6mths','acc_open_past_24mths','mo_sin_old_rev_tl_op','mo_sin_rcnt_rev_tl_op','earliest_cr_line','total_rev_hi_lim','avg_cur_bal','bc_open_to_buy','tot_hi_cred_lim','total_bal_ex_mort','total_il_high_credit_limit','num_op_rev_tl']

for d in drops3:
    loans.drop(d, axis=1, inplace=True)


loans = loans[np.isfinite(loans['loan_amnt'])]

# Mean, median, and mode substitutions
loans["emp_title"].fillna("Not provided", inplace=True)
loans["annual_inc"].fillna(loans["annual_inc"].mean(), inplace=True)
loans["title"].fillna("Debt consolidation",inplace=True) # mode
loans["mths_since_last_delinq"].fillna(loans['mths_since_last_delinq'].max(),inplace=True)
loans["mths_since_recent_inq"].fillna(loans["mths_since_recent_inq"].median(),inplace=True)


# For remaining columns, the number of missing values are very small relative to the size of the data set so we are dropping the rows with missing values
loans.dropna(subset=['zip_code'], inplace=True)
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

# Convert format of interest rates
loans['int_rate'] = loans['int_rate'].map(lambda a: float(a.strip('%')))

output='loanstats.csv'
loans.to_csv(output, index=False)
print("Success!")