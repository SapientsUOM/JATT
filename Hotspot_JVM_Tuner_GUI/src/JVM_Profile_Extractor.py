'''
This profiler uses jstat on 12/12/2014
The processing may be changed with jstat version
'''

import sys
import subprocess
import re
import time
import pandas as pd
import numpy as np
import argparse
import os

argparser = argparse.ArgumentParser()
argparser.add_argument('--RunCommand',help='Command to Run the Java file in order to collect profile data')
argparser.add_argument('--ProgramName',help='What to search when executing the Java file inorder to indentify the process id')
argparser.add_argument('--RunType',help='Run Type Specifies default or tuned')


'''
java -jar dacapo-9.12-bach.jar avrora -n 1

'''
class JVMProfiler:
    
    def __init__(self,optionset,program,benchmark):
	self.name = 'JVM_Profiler'
        self.options = optionset
        #self.java_program_run_command='java -jar dacapo-9.12-bach.jar '+program+' -n 1'
        self.java_program_run_command=program
        self.final_df=pd.DataFrame()
	if not os.path.exists('jstat_temp_files/'):
		os.makedirs('jstat_temp_files')
		
	
        
        
    def getProfileData(self,tag,program,benchmark,interval,samples,runtype):
        java_process=subprocess.Popen(self.java_program_run_command,stdout=subprocess.PIPE,shell=True)
	#print self.java_program_run_command
	#time.sleep(2)
        optionset = self.options
        p = subprocess.Popen('ps -ef | grep java > jstat_temp_files/vmstat.txt', stdout=subprocess.PIPE, shell=True)
        p_status = p.wait()
        f = open ('jstat_temp_files/vmstat.txt','r')
        lines = f.readlines()
        f.close()
        subprocesses = []
        subprocesses.append(java_process) 
	#time.sleep(5)
        for line in lines:
            if ((str(benchmark) or str(':XX') in line) and ('python' not in line) and ('/bin/sh' not in line)):
                print 'found = ',line
                words = re.split("\s+", line)
                process_ID = words[1]
                '''
                Run the subprocesses
                '''
                print 'process id = ',process_ID
                for option in optionset:
                    jstat_command = 'jstat -'+str(option)+' '+str(process_ID)+' '+str(interval)+' '+str(samples)
                    print 'jstat command = ',jstat_command,'for benchmark = ',benchmark
                    
                    p = subprocess.Popen(jstat_command + ' > jstat_temp_files/jstat_'+str(benchmark)+'_'+str(option)+str(runtype)+'.txt', stdout=subprocess.PIPE, shell=True)
                    subprocesses.append(p)
                for p in subprocesses:
                    status = p.wait()
                time.sleep(5)
                break 
            
        _class = 'Loaded,LoadedBytes,Unloaded,UnloadedBytes,ClassTime'
        compiler = 'Compiled,Failed,Invalid,CompilerTime'
        gc='S0C,S1C,S0U,S1U,EC,EU,OC,OU,PC,PU,YGC,YGCT,FGC,FGCT,GCT'
        
        coldict = {'class' : _class, 'compiler':compiler, 'gc':gc}
        for option in optionset:  
            file = open('jstat_temp_files/jstat_'+str(benchmark)+'_'+str(option)+str(runtype)+'.txt','r')
            stat_lines = file.read().splitlines()
            file.close()
            for linenum in range(0,len(stat_lines)):
                    line = stat_lines[linenum]
                    line = re.sub('\s+',',',line)
                    if linenum !=0:
                        line = line[1:]
                    else:
                        linelist = list(line)
                        if linelist[0] == ',':
                            linelist[0]=''
                        line="".join(linelist)
                        stat_lines[linenum] = line
						
                        #print type(line)
                    if option == 'compiler':
                        commas = line.count(',')
                        if commas > 5:
                            lastcomma = line.rfind(',')
                            listline = list(line)
                            listline[lastcomma] = '/'
                            line="".join(listline)
                    stat_lines[linenum] = line
            if option == 'compiler':
                stat_lines[0]='Compiled,Failed,Invalid,CompilerTime,FailedType,FailedMethod'
            if option =='class':
                stat_lines[0]='Loaded,LoadedBytes,Unloaded,UnloadedBytes,ClassTime'
            statfile = open ('jstat_temp_files/jstat_'+str(benchmark)+'_'+str(option)+str(runtype)+'.csv','w')
            statfile.write("\n".join(stat_lines))
            
    def getStatistics(self,program,benchmark,runtype):
        optionset = ['gc','compiler','class']
        dataframe_dict = {}
        _class = ['Loaded','LoadedBytes','Unloaded','UnloadedBytes','ClassTime']
        compiler = ['Compiled','Failed','Invalid','CompilerTime']
        gc=['S0C','S1C','S0U','S1U','EC','EU','OC','OU','PC','PU','YGC','YGCT','FGC','FGCT','GCT']
        coldict = {'class' : _class, 'compiler':compiler, 'gc':gc}
        
        for option in optionset:
            #print option
            dataframe_dict[option] = pd.read_csv('jstat_temp_files/jstat_'+str(benchmark)+'_'+str(option)+str(runtype)+'.csv',usecols=coldict[option])
	gcdf =  dataframe_dict['gc']
	gcdf['HU']=(gcdf.S0U+gcdf.S1U+gcdf.EU+gcdf.OU+gcdf.PU)*100/(gcdf.S0C+gcdf.S1C+gcdf.EC+gcdf.OC+gcdf.PC)
	
	jitdf=dataframe_dict['compiler']
	jitdf['CR']=jitdf.Compiled*100/jitdf.CompilerTime
	
	classdf=dataframe_dict['class']
	classdf['CLR']=classdf.Loaded*100/classdf.ClassTime
	
	dataframe_dict['gc']=gcdf
	dataframe_dict['compiler']=jitdf
	dataframe_dict['class']=classdf
	
	for option in optionset:
            #print option
            dataframe_dict[option].to_csv('jstat_temp_files/jstat_'+str(benchmark)+'_'+str(option)+str(runtype)+'.csv',index=False)	
	
        
    
        
if __name__ == '__main__':

    #programs = ['sunflow','avrora','jython','h2','','luindex','lusearch','pmd','sunflow','tomcat','tradebeans','tradesoap','xalan']
    #file = open('OptimizedConfigurations/'+'ALL.txt',"r")
    args=argparser.parse_args()
    
	
	
    optionset = ['gc','compiler','class'] 
    profiler = JVMProfiler(optionset,args.RunCommand,args.ProgramName)
    profiler.getProfileData('dacapo',args.RunCommand,args.ProgramName,10,'',args.RunType)
    profiler.getStatistics(args.RunCommand,args.ProgramName,args.RunType)
    
    
    
        
    '''
    program = programs[4] 
    profiler = JVMProfiler(optionset,program)
    profiler.getProfileData('dacapo',program,250,100)
    profiler.getStatistics(program)   
    '''
