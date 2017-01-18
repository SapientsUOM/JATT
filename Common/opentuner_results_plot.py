# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib as mp
import pandas as pd
import sqlite3 as sq
import matplotlib.pyplot as plt
import sys
import os
import pylab
import argparse

# <codecell>

argparser = argparse.ArgumentParser()
argparser.add_argument('--plot_output',default='',help='specify the plot output location')
argparser.add_argument('--db_folder_path',default='',help='specify the folder location of db')
argparser.add_argument('--db_file_name',default='',help='specify name of db')

# <codecell>

# args = argparser.parse_args()
# folderpath = args.db_folder_path
# #raw_input("Enter folder name: ")
# database_filename = args.db_file_name
# #raw_input("Enter database file name (with .db): ")

folderpath='../cse-B85-HD3'
database_filename='cse-B85-HD3.db'


if len(folderpath)>0:
	databasepath = str(folderpath) + '/'+str(database_filename)
else:
	databasepath= str(database_filename)

# <codecell>

connection = sq.connect(databasepath)

# <codecell>

project_cursor = connection.cursor()
project_cursor.execute('SELECT id,name FROM program')
project_table = pd.DataFrame(columns=['program_id','program_name'],index=None)
for project in project_cursor:
    project_table.loc[len(project_table)]=[project[0],project[1]] 
    
firstrow=project_table.head()

# <codecell>

N=firstrow.program_name.count()
for i in range(N):
    row_project_name = str(firstrow.program_name[i])
    row_project_id = str(firstrow.program_id[i])
    configuration_cursor = connection.cursor()
    program_id_val = (row_project_id,)
    configuration_cursor.execute('SELECT id,time,result_id FROM (SELECT id FROM configuration where program_id = ?) INNER JOIN  (SELECT id as result_id,configuration_id, [time] FROM result WHERE time is not 10000.0) ON id = configuration_id',program_id_val)
    df= pd.DataFrame(columns=['config_id','time','result_id'])
    index_no=[]
    counter = 0
    for row in configuration_cursor:
        counter = counter+1
        index_no.append(counter)
        df.loc[len(df)]=[row[0],row[1],row[2]]
    
    
    df.time=100/df.time
    df_result_id = df.sort('result_id')
    df_time = df.sort('time')
    
    plt.clf()
    plt.scatter(index_no, df_result_id.time)
    plt.ylabel('run time in ops_per_min')
    plt.xlabel('result index')
    plt.grid(True)
    plt.savefig('plots/sorted_result_id_'+row_project_name+'.pdf')
    
    plt.clf()
    plt.scatter(index_no,df_time.time)
    plt.ylabel('run time in ops_per_min')
    plt.xlabel('result index')
    plt.grid(True)
    plt.savefig('plots/sorted_opes_per_min'+row_project_name+'.pdf')

# <codecell>


