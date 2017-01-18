'''
#Author:SapientS
#Date:30/10/2014
#This file contains some simple functionalities which needed to perform the JVM tuner. 
#SapientS
'''

import threading
import paramiko
import time
import re
import sys
import subprocess
import os

class TomcatHelper():

    def __init__(self, warfilename, servlet,requests,ip,username,password):
        self.ip = str(ip)
        self.user_name = str(username)
        self.password = str(password)
        self.tomcat_bin_location = '~/SapientS/hotspottuner/TomcatTuner/src/apps/tomcat/bin/'
        self.local_catalina_location = 'apps/tomcat/bin/catalina.sh'
        self.remote_catalina_location = '/home/cse/SapientS/hotspottuner/TomcatTuner/src/apps/tomcat/bin/catalina.sh'
        self.default_run_time = 0
        #self.ab_command =  'ab -k -n 100000 -c 149 http://'+self.ip+':8080/sample/hello'
        self.ab_command =  'ab -k -n '+str(requests)+' -c 149 http://'+self.ip+':8080/'+str(warfilename)+'/'+str(servlet)
        '''
        Give the locations correctly
        '''
        self.jmeter_command = 'java -jar apps/apache_jmeter/bin/ApacheJMeter.jar -n -t apps/apache_jmeter/bin/examples/PerformanceTestPlanMemoryThread.jmx > apps/apache_jmeter/bin/jmeter_result.txt'
        self.sleep_time = 20
        
    
    def open_ssh_connection(self):
        self.ssh  = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip,username=self.user_name,password=self.password)
        
        
    def get_default_runtime(self):
        
        self.set_catalinash('')
        run_command = 'sh '+self.tomcat_bin_location+'startup.sh'
        stdin, stdout, stderr = self.ssh.exec_command(run_command)
        time.sleep(self.sleep_time)
    
        time_per_request = self.read_respond(True)
        self.default_run_time= time_per_request
        print 'self.default_run_time = ',time_per_request
        time.sleep(self.sleep_time)
        
        run_command = 'sh '+self.tomcat_bin_location+'shutdown.sh'
        stdin, stdout, stderr =self.ssh.exec_command(run_command)
        time.sleep(self.sleep_time)
        
        f = open('tomcat_configuration.txt',"a")
        f.write(run_command)
        f.write('self.default_run_time = '+str(self.default_run_time)+'\n')
        f.close()
        
        return self.default_run_time
   
    def read_jmeter_respond (self):
        jmeter_output = ''
        
        p = subprocess.Popen(self.jmeter_command, stdout=subprocess.PIPE, shell=True)
#        (output, err) = p.communicate()
        p_status = p.wait()
        

        f = open('apps/apache_jmeter/bin/jmeter_result.txt',"r")
        jmeter_output = f.readlines()
        final_summary_line_number=0
        '''
        The following loop is not necessary if we are sure
        that the final result is always two lines before the end of file
        '''
        for linenum in range(len(jmeter_output)-1,0,-1):
            if "Tidying up" in jmeter_output[linenum]:
                final_summary_line_number = linenum - 1
                break
        
        final_summarry_line = jmeter_output[final_summary_line_number]   
        print 'final_summary = \n',final_summarry_line
        
        if len(final_summarry_line)>0:
            m = re.search('Avg:(.*) Min:.*', final_summarry_line,flags=re.DOTALL)
            err = re.search('Err: .*(\((.*)%\))',final_summarry_line,flags=re.DOTALL)

            jmeter_bench_time = '10000'
        else: 
            print 'Error running jmeter or reading the result file. In the run function >> read_jmeter_respond'
            sys.exit()
        if m:
            jmeter_bench_time = m.group(1)
            if err:
                j_meter_err = err.group(2)
                if float(j_meter_err) > 50:
                    jmeter_bench_time  = 10000
        try:
            time_per_request = float(jmeter_bench_time)
        except:
            time_per_request=10000
            print 'jmeter respond has not found proper value.In the run function >> read_jmeter_respond\nTuning aborting...'
            sys.exit()   
            
        return time_per_request        
        
 
    def read_respond (self):
        ab_bench_output = ''
        
        p = subprocess.Popen(self.ab_command, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        
        ab_bench_output = output
        print 'ab_bench_output defaultruntime = ',ab_bench_output
        if len(ab_bench_output)>0:
            m = re.search('Time per request(.*)\[ms\] \(mean\)', ab_bench_output,flags=re.DOTALL)
            ab_bench_time = '10000'
        else: 
            print 'Error running ab. In the run function.'
            sys.exit()
        if m:
            ab_bench_time = m.group(1)
        ab_bench_time = re.sub(':', '', ab_bench_time,flags=re.DOTALL) 
        try:
            time_per_request = float(ab_bench_time)
        except:
            time_per_request=10000
            print 'ab respond has not found proper value.Tuning aborting...'
            sys.exit()   
            
        return time_per_request
    
    def set_catalinash(self,flags):
        #text = # OPENTUNER JVM SETTINGS STARTED.......# OPENTUNER JVM SETTINGS END
        self.open_ssh_connection()
        if(os.path.isfile(self.local_catalina_location)):
            cat_sh = open(self.local_catalina_location,"r")
            cat_text = cat_sh.read()
            if len(flags)>0:
                cat_text = re.sub('# OPENTUNER JVM SETTINGS STARTED.*# OPENTUNER JVM SETTINGS END', '# OPENTUNER JVM SETTINGS STARTED\nCATALINA_OPTS="'+flags+'"\n# OPENTUNER JVM SETTINGS END', cat_text,flags=re.DOTALL)       
                cat_text = re.sub('#OPENTUNER JVM SETTINGS END.*# OS specific support.  $var _must_ be set to either true or false.', '', cat_text,flags=re.DOTALL)
            else:
                print 'in set_catalinash setting with empty flag.'
                cat_text = re.sub('# OPENTUNER JVM SETTINGS STARTED.*# OPENTUNER JVM SETTINGS END', '# OPENTUNER JVM SETTINGS STARTED\n# OPENTUNER JVM SETTINGS END', cat_text,flags=re.DOTALL)
                cat_text = re.sub('#OPENTUNER JVM SETTINGS END.*# OS specific support.  $var _must_ be set to either true or false.', '', cat_text,flags=re.DOTALL)
            cat_sh.close()
            cat_sh = open(self.local_catalina_location,"w")
            cat_sh.write(cat_text)
            cat_sh.close()
            sftp = self.ssh.open_sftp()
            sftp.put(self.local_catalina_location,self.remote_catalina_location )
    
    def run_command(self,flags,type):
        self.set_catalinash(flags)
        print 'Catalina sh is set with flags.'
        run_command = 'sh '+self.tomcat_bin_location+'startup.sh'
        stdin, stdout, stderr = self.ssh.exec_command(run_command)
        time.sleep(self.sleep_time)
        
        '''
        First iteration is ignored
        '''
        invalid_config_found = False
        if type == 'ab':     
            print 'Calling ab benchmark.Plese wait...\n'
            time_per_request = self.read_respond()
        else:
            print 'Calling jmeter benchmark.Plese wait...\n'
            time_per_request = self.read_jmeter_respond()
        print 'time_per_request for the first request = ' , time_per_request
        
        
        if time_per_request==10000:
            invalid_config_found = True
        
        '''
        Iterations from here are calculated.
        '''
            
        temp_metric = 0    
        local_time_per_request = 0
        
        if invalid_config_found == False:
            
            for i in range(0,2):
                print 'calculating in the iteration ', i
                if type == 'ab':
                    print 'Calling ab benchmark.Plese wait...\n'
                    local_time_per_request = float(self.read_respond())
                else:
                    print 'Calling jmeter benchmark.Plese wait...\n'
                    local_time_per_request = float(self.read_jmeter_respond())
                
                if local_time_per_request == 10000:
                    self.set_catalinash('')
                    time_per_request = local_time_per_request
                    print 'Invalid config found. time_per_request for the first request = ' , time_per_request
                    invalid_config_found = True
                    break
                
                temp_metric += float(local_time_per_request)
                
        if invalid_config_found == False:
            time_per_request = temp_metric/2
            print 'time_per_request mean = ' , time_per_request
        
        
        
        run_command = 'sh '+self.tomcat_bin_location+'shutdown.sh'
        stdin, stdout, stderr =self.ssh.exec_command(run_command)
        time.sleep(self.sleep_time)
        print 'Run function returned successfully. Time per request:=>'+str(time_per_request)
        return time_per_request

    