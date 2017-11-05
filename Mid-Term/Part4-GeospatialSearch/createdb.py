#import MySQLdb as sql
import sys
import csv
import pandas as pd


db = pd.read_csv('../Part1-EDA/clean_data.csv', low_memory=False)


#con = sql.connect('properties.db')
#cur = con.cursor()
#cur.execute('DROP TABLE Properties;')
#cur.execute('CREATE TABLE Properties(propertyid varchar(255),latitude float,longitude float)')

#for index, row in db.iterrows():
#    cmd = 'INSERT into Properties values (' + str(row['parcelid']) + ',' + str(row['latitude']) + ',' + str(row['longitude']) + ');'
#    cur.execute(cmd)

#con.close()


db2 = db['parcelid','latitude','longitude']
db2.to_csv('latlon.csv', index=False)
