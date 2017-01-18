import paramiko
import time
import re
import os
import argparse
import abc

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser],add_help=False)
argparser.add_argument('--local_catalina_location',
                       help='Give the location of catalina.sh file in local machine')
argparser.add_argument('--remote_catalina_location',
                       help='Give the location of bin directory in tomcat server machine')
argparser.add_argument('--remote_tomcat_bin_loc',
                       help='Give the location of bin directory in tomcat server machine')
argparser.add_argument('--ssh_username',
                       help='In order to login to remote machine, provide ssh username')
argparser.add_argument('--ssh_password',
                       help='Password for user given in ssh username')
argparser.add_argument('--server_ip', 
                       help='IP address for tomcat server')
argparser.add_argument('--sleep_time', 
                       help='additional time to start tomcat')
class TomcatTunerAbstract(JvmFlagsTunerInterface):
    
    __metaclass__ = abc.ABCMeta

    def __init__(self,args, *pargs, **kwargs):
        super(TomcatTunerAbstract, self).__init__(args, *pargs,
                                        **kwargs)
        self.args = args
        
    def open_ssh_connection(self):
        self.ssh  = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.args.server_ip,username=self.args.ssh_username,password=self.args.ssh_password)
        
    def set_catalinash(self):
        self.open_ssh_connection()
        if(os.path.isfile(self.args.local_catalina_location)):
            cat_sh = open(self.args.local_catalina_location,"r")
            cat_text = cat_sh.read()
            if len(self.flags)>0:
                cat_text = re.sub('# OPENTUNER JVM SETTINGS STARTED.*# OPENTUNER JVM SETTINGS END', '# OPENTUNER JVM SETTINGS STARTED\nCATALINA_OPTS="'+self.flags+'"\n# OPENTUNER JVM SETTINGS END', cat_text,flags=re.DOTALL)       
                cat_text = re.sub('#OPENTUNER JVM SETTINGS END.*# OS specific support.  $var _must_ be set to either true or false.', '', cat_text,flags=re.DOTALL)
            else:
                print 'in set_catalinash setting with empty flag.'
                cat_text = re.sub('# OPENTUNER JVM SETTINGS STARTED.*# OPENTUNER JVM SETTINGS END', '# OPENTUNER JVM SETTINGS STARTED\n# OPENTUNER JVM SETTINGS END', cat_text,flags=re.DOTALL)
                cat_text = re.sub('#OPENTUNER JVM SETTINGS END.*# OS specific support.  $var _must_ be set to either true or false.', '', cat_text,flags=re.DOTALL)
            cat_sh.close()
            cat_sh = open(self.args.local_catalina_location,"w")
            cat_sh.write(cat_text)
            cat_sh.close()
            sftp = self.ssh.open_sftp()
            sftp.put(self.args.local_catalina_location,self.args.remote_catalina_location )
        else:
            print 'Could not find the local catalina file'
            
    def start_tomcat_server(self):
        self.set_catalinash()
        print 'Catalina sh is set with flags.'
        run_command = 'sh '+self.args.remote_tomcat_bin_loc+'startup.sh'
        stdin, stdout, stderr = self.ssh.exec_command(run_command)
        time.sleep(float(self.args.sleep_time))
        
    def shutdown_tomcat_server(self):
        run_command = 'sh '+self.args.remote_tomcat_bin_loc+'shutdown.sh'
        stdin, stdout, stderr =self.ssh.exec_command(run_command)
        time.sleep(float(self.args.sleep_time))
    
    @abc.abstractmethod    
    def run_benchmark(self):
        """
        Child classes must implement this
        method to execute their benchmark
        and this method should return runtime from
        the benchmark
        """
        return 0
    
    def execute_program(self):
        self.start_tomcat_server()
        '''
        First iteration can be ignored
        If iterations are more than 1, first iteration will
        be ignored
        '''
        time_per_request = self.run_benchmark()
        if(time_per_request == 10000):
            self.shutdown_tomcat_server()
            return time_per_request
        
        if(int(self.args.iterations) == 1):
            self.shutdown_tomcat_server()
            return float(time_per_request)
        
        temp_metric = 0    
        local_time_per_request = 0
        
        for i in range (0,int(self.args.iterations-1)):
            local_time_per_request = float(self.run_benchmark())
            if local_time_per_request == 10000:
                self.shutdown_tomcat_server()
                return local_time_per_request
            temp_metric += local_time_per_request
            
        time_per_request = temp_metric/(int(self.args.iterations)-1)
        
        self.shutdown_tomcat_server()
        return time_per_request
        