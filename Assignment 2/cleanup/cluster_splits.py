import pandas as pd
from sklearn.externals import joblib
from sklearn import cluster
import pickle

#loans = pd.read_csv('../loanstats.csv')
loans = pd.read_csv('loans_clean.csv')


#loans.drop('grade', axis=1, inplace=True)
#loans.drop('sub_grade', axis=1, inplace=True)
#loans.drop('set', axis=1, inplace=True)
#loans.drop('timestamp', axis=1, inplace=True)

#loans.to_csv('loans_clean.csv', index=False)


k_means = joblib.load(open('kmeans.pkl', 'rb'))
loans['kcluster'] = k_means.labels_


kc0 = loans[loans['kcluster']==0]
kc1 = loans[loans['kcluster']==1]
kc2 = loans[loans['kcluster']==2]
kc3 = loans[loans['kcluster']==3]
kc4 = loans[loans['kcluster']==4]
kc5 = loans[loans['kcluster']==5]
kc6 = loans[loans['kcluster']==6]

kc0.drop('kcluster', axis=1, inplace=True)
kc1.drop('kcluster', axis=1, inplace=True)
kc2.drop('kcluster', axis=1, inplace=True)
kc3.drop('kcluster', axis=1, inplace=True)
kc4.drop('kcluster', axis=1, inplace=True)
kc5.drop('kcluster', axis=1, inplace=True)
kc6.drop('kcluster', axis=1, inplace=True)

kc0.to_csv('kmeans0.csv', index=False)
kc1.to_csv('kmeans1.csv', index=False)
kc2.to_csv('kmeans2.csv', index=False)
kc3.to_csv('kmeans3.csv', index=False)
kc4.to_csv('kmeans4.csv', index=False)
kc5.to_csv('kmeans5.csv', index=False)
kc6.to_csv('kmeans6.csv', index=False)

loans.drop('kcluster', axis=1, inplace=True)

def manual_clusters(fico):
    if fico > 720:
        return 'Group1'
    elif fico > 700:
        return 'Group2'
    elif fico > 690:
        return 'Group3'
    elif fico > 680: # amnt < 25000
        return 'Group4'
    elif fico > 670:
        return 'Group5'
    else:
        return 'Group6'

loans['manual_cat'] = loans.apply(lambda x: manual_clusters(x['fico_range_low']), axis=1)

man1 = loans[loans['manual_cat']=='Group1']
man2 = loans[loans['manual_cat']=='Group2']
man3 = loans[loans['manual_cat']=='Group3']
man4 = loans[loans['manual_cat']=='Group4']
man5 = loans[loans['manual_cat']=='Group5']
man6 = loans[loans['manual_cat']=='Group6']

man1.drop('manual_cat',axis=1,inplace=True)
man2.drop('manual_cat',axis=1,inplace=True)
man3.drop('manual_cat',axis=1,inplace=True)
man4.drop('manual_cat',axis=1,inplace=True)
man5.drop('manual_cat',axis=1,inplace=True)
man6.drop('manual_cat',axis=1,inplace=True)

man1.to_csv('manual1.csv', index=False)
man2.to_csv('manual2.csv', index=False)
man3.to_csv('manual3.csv', index=False)
man4.to_csv('manual4.csv', index=False)
man5.to_csv('manual5.csv', index=False)
man6.to_csv('manual6.csv', index=False)
