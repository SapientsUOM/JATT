import argparse
import re
import os

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
argparser.add_argument('--path',default='',help='benchmark path e.g KMEANS/')
argparser.add_argument('--np',default='10',help='Number of places ; default=10')
argparser.add_argument('--main',default='',help='Main class in the .jar file')
argparser.add_argument('--other',default='',help='Other Parameters needed by the jar file. ')
argparser.add_argument(
  '--x10bench', default='x10 -np {np} {Opt_flags} -cp {path}{source}.jar {main} {other}',
  help='Command template to execute an x10 benchmark... automatically generated by the specified parameters.')


class x10Tuner(JvmFlagsTunerInterface):
    
    def __init__(self, *pargs, **kwargs):
               
        super(x10Tuner, self).__init__(args, *pargs,
                                        **kwargs)
                
    def execute_program(self):
        temp_metric = 0
        args.iterations=3;
        if(not(os.path.isfile(args.path+args.source+'.jar'))):
           self.x10_buid_command='sh {path}build-managed'
           print 'x10 benchmark build'
           self.x10_buid_command=self.x10_buid_command.format(path=args.path);
           self.call_program(self.x10_buid_command);
           print 'x10 benchmark build complete' 
        if self.flags:
            x10_Java_flags=re.sub('-XX:','-J-XX:',self.flags)
            self.flags=x10_Java_flags
            self.x10_exe_command=args.x10bench.format(np=args.np,Opt_flags=x10_Java_flags,path=args.path,source=args.source,main=args.main,other=args.other)
        else:
            self.x10_exe_command=args.x10bench.format(np=args.np,Opt_flags=self.flags,path=args.path,source=args.source,main=args.main,other=args.other)    
        for i in range(0,int(args.iterations)):
            if self.runtime_limit>0:
                print 'Execution with run time limit...'
                run_result = self.call_program(self.x10_exe_command,limit=self.runtime_limit)
            else:
                run_result = self.call_program(self.x10_exe_command)
		#print run_result
            temp_metric += self.get_ms_x10benchmark(run_result['stdout'])
            #print run_result 
        temp_metric=float(temp_metric/int(args.iterations))
        return temp_metric
    
    def get_ms_x10benchmark(self,result):
        #m=re.search('Total time: [0-9]*.[0-9]*', result, flags=re.DOTALL)
        m=re.search('CPU time used: [0-9]*.[0-9]*',result,flags=re.DOTALL)
        m_sec=1000000 #Value taken in case of any error.
        if m:
            m_sec=m.group(0)
            #m_sec=re.sub('Total time: ', '',m_sec)
            m_sec=re.sub('CPU time used: ','',m_sec)
            try:
                m_sec=float(m_sec)
            except:
                m_sec=1000000
        return m_sec
        
if __name__ == '__main__':
    args = argparser.parse_args()
    x10Tuner.main(args)
