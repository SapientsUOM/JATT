import sqlite3 as sq
import joblib as jb

#Give the correct path to the database file from here 
databasepath = 'cse-B85-HD3_ant_colony_5Iterations.db'
#Give the file name of the intended output file
resultfile_name = 'config.txt'
conn = sq.connect(databasepath)
cursor = conn.cursor()
cursor.execute('''SELECT data from configuration''')
result = open(resultfile_name,"w")
result.close()
counter = 1
for row in cursor:
	pklfile = open('pickle.pkl',"w")
	pklfile.write(row[0])
	pklfile.close()
        datablob = jb.load('pickle.pkl')
	resultfile = open(resultfile_name,"a")
	resultfile.write('\n\n'+str(counter)+str(datablob))
	counter = counter +1
	resultfile.close()
