# -*- coding: utf-8 -*-
'''
@Author:Sapients
@Date:14/02/2015
@To generate jstat graphs from raw data. 

'''


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os as os

argparser = argparse.ArgumentParser()
argparser.add_argument('--CSVDefault',help='Name of the file which contains the plotting data of default configuration')
argparser.add_argument('--CSVTuned',help='Name of the file which contains the plotting data of tuned configuration')
argparser.add_argument('--Property',help='Which property to plot')
argparser.add_argument('--Interval',help='Interval of the jstat data profiling',default='10')
argparser.add_argument('--Output',help='Output file name',default='figure')

args=argparser.parse_args()

prop_names={'CLR':'Class Loading Rate (per ms)','CR':'Compiler Rate (per ms)','HU':'Overall Heap Utilization %','GCT':'Garbage Collection Time'}
prop=args.Property
inter=float(args.Interval)

def read_data(filepath,interval,prop):
    Y=[]
    X=[]
    count=0
    interval=10
    if os.path.isfile(filepath):
        df_default=pd.read_csv(filepath)
        Y=np.array(df_default[prop])
        for i in range(0,len(Y)):
           X.append(count+interval)
           count=count+interval
    return X,Y


X_def,Y_def=read_data(filepath=args.CSVDefault,prop=prop,interval=inter)
X_tun,Y_tun=read_data(filepath=args.CSVTuned,prop=prop,interval=inter)


plt.title('Jstat Profiler '+prop_names[prop])
plt.grid(True)
plt.xlabel('Time (ms)')
plt.ylabel(prop_names[prop])
plt.plot(X_def,Y_def,'b')
plt.plot(X_tun,Y_tun,'r')

plt.savefig(args.Output+'.jpg')
plt.show()




