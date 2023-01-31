# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 14:49:25 2022

@author: Elliot

Run this code from root folder. This code will 
1. Import Covid Cases data from the U.S. CDC website, 
U.S. Census ACS 5-Year Survey 2019 and ANSI Codes for States 
stored as CSV files in the `.\datasets` folder.  
2. Load all three datasets into an SQLite database.
3. Execute a version of the `.\src\covid19_ETL.sql` query modified 
for SQLite to join datasets and calculate total Covid cases 
in the past 14-day for each state over through time.
4. Output a file with the query results into a file named `US_MMM_DD.csv`
in the `.\datasets\Generated` folder, where MMM is the abbreviation of
current month and DD is the current day.

The output file can be used to create mentioned Tableau Visualization.

"""

import requests
import sqlite3
import numpy as np
import pandas as pd
import datetime as dt
import os

con = sqlite3.connect('covid_cases.db',
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES)

# Use Requests to get latest Covid data
covid_data = requests.get('https://data.cdc.gov/api/views/9mfq-cb36/rows.csv')

covid_data_txt = [s for i,s in enumerate(covid_data.text.split('\n'))]

covid_data_text_list = []
for i in covid_data_txt[1:len(covid_data_txt)-1]:
    covid_data_text_list.append(tuple(i.split(',')))
    
    
# Create SQL table for Covid cases
cur = con.cursor()

todate = dt.date.today().strftime('%b_%d')
db_name = 'cdc_covid_cases_' + todate
dropdb_q = 'DROP TABLE IF EXISTS ' + db_name

cur.execute(dropdb_q)


# Create Covid Data Table
cases_query = "CREATE TABLE "+ db_name + " (" + (' text,'.join(covid_data_txt[0].split(',')))+ " text)"

cur.execute(cases_query)


# Insert Data into table
covid_data_text_list = []
for i in covid_data_txt[1:len(covid_data_txt)-1]:
    covid_data_text_list.append(tuple(i.split(',')))

insert_q = 'INSERT INTO {} VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'.format(db_name)
cur.executemany(insert_q, covid_data_text_list)

con.commit()


# Load State Abbreviations from text file
state_abbrev = []
with open(os.path.join('datasets','state_abbrev.txt')) as f:
    for i,l in enumerate(f.readlines()):
        state_abbrev.append(','.join(l.strip('\n').split('|')))
        
f.close()


# Create state_abbrev table in Current Database

cur.execute('DROP TABLE IF EXISTS state_abbreviations')

cur.execute('CREATE TABLE state_abbreviations (STATE INTEGER,STUSAB text,STATE_NAME text,STATENS INTEGER)')

state_abb_list = []
for i in state_abbrev:
    state_abb_list.append(tuple(i.split(',')))

con.executemany('INSERT INTO state_abbreviations VALUES (?,?,?,?)', state_abb_list[1:])

con.commit()


# Load Census Data from local csv file
census = []
with open(os.path.join('datasets','ACSST5Y2019.S0101_2022-01-14T174326','ACSST5Y2019.S0101_data_with_overlays_2021-12-10T154120.csv')) as f:
    for i,l in enumerate(f.readlines()):
        census.append(l)
f.close()

census = census[1:]


# Clean data
census[0] = census[0].replace('!','_',).replace(' ','_')


# Create data tuples to load into SQL table.  Use only 16 columns
census_list = []
for i in census[1:]:
    temp = []
    for attr in i.split(','):
        temp.append(attr.strip('"'))
    census_list.append(tuple(temp)[:16])
    
    
# Create data tuples to load into SQL table.  Use only 16 columns
census_list = []
for i in census[1:]:
    temp = []
    for attr in i.split(','):
        temp.append(attr.strip('"'))
    census_list.append(tuple(temp)[:16])
    

# Prepare Columns for census data table
census_col_name = []
for i in census[0].split(','):
    census_col_name.append(i)
    
a = ("INTEGER|"*16).split('|')

for i in [0,1,3]:
    a[i] = 'TEXT'  
    

# Create SQLite table
census_query = 'CREATE TABLE acs_5Y_2019 ('

for x,y in zip(census_col_name[:16], a):
    census_query += x + ' '+ y + ','
census_query = census_query[:-1] + ');'
census_query

cur.execute('DROP TABLE IF EXISTS acs_5Y_2019')
cur.execute(census_query)

con.executemany('INSERT INTO acs_5Y_2019 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', census_list)

con.commit()


# Query Datasets

with open(os.path.join('src','covid19_ETL.sql')) as ETL:
    data_combine_query = ETL.read()

ETL.close()


# Change BigQuery Database names to match SQLite Database names
data_combine_query = data_combine_query.replace(
                        '`coursera-analytics-class.covid_by_percent.cdc_covid_cases_Jan_19`', 
                        db_name)

data_combine_query = data_combine_query.replace(
                        '`coursera-analytics-class.covid_by_percent.',
                        '')

data_combine_query = data_combine_query.replace('`', '')

# Change Date Casting methods to work in SQLite
data_combine_query = data_combine_query.replace("CAST(REPLACE(submission_date, '/', '-') AS DATE FORMAT 'MM-DD-YYYY')",
                                                'DATE(SUBSTR(submission_date,7,4)||"-"||SUBSTR(submission_date,1,2)||"-"||SUBSTR(submission_date,4,2))')

data_combine_query = data_combine_query.replace(
                                        "CAST(REPLACE(cdc.submission_date, '/', '-') AS DATE FORMAT 'MM-DD-YYYY')",
                                        'DATE(SUBSTR(cdc.submission_date,7,4)||"-"||SUBSTR(cdc.submission_date,1,2)||"-"||SUBSTR(cdc.submission_date,4,2))')

# Change Float Casting methods to work in SQLite
data_combine_query = data_combine_query.replace("cs.new_cases/pop.Estimate__Total__Total_population",
                                                """CAST(cs.new_cases AS REAL)/(CAST(pop.Estimate__Total__Total_population AS REAL))""")

data_combine_query = data_combine_query.replace("rc.sum_cases_last_14_days/pop.Estimate__Total__Total_population",
                                                """CAST(rc.sum_cases_last_14_days AS REAL)/(CAST(pop.Estimate__Total__Total_population AS REAL))""")

data_combine_query = data_combine_query.replace('LEFT JOIN', 'INNER JOIN')

cur.execute(data_combine_query).fetchall()


# Use Pandas to execute query and write to a data frame
db_df = pd.read_sql_query(data_combine_query, con)

# Use Pandas to write df to csv
output_path = os.path.join('datasets','Generated','US_'+dt.date.today().strftime('%b_%d')+'.csv')
db_df.to_csv(output_path, index=False)


# Close db connection
con.close()

print('Output file in <{}>'.format(output_path))
