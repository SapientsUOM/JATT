import argparse
import re
import os

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
# argparser.add_argument('--path',default='',help='benchmark path e.g KMEANS/')
# argparser.add_argument('--np',default='10',help='Number of places ; default=10')
# argparser.add_argument('--main',default='',help='Main class in the .jar file')
# argparser.add_argument('--other',default='',help='Other Parameters needed by the jar file. ')
argparser.add_argument(
  '--debs', default='sh ./run.sh {data_location} 1024 {Opt_flags}',
  help='Command template to execute the debs code.')


class debsTuner(JvmFlagsTunerInterface):
    
    def __init__(self, *pargs, **kwargs):
               
        super(debsTuner, self).__init__(args, *pargs,
                                        **kwargs)
                
    def execute_program(self):
        temp_metric = 0
        args.iterations=1;
                
        self.debs_command=args.debs.format(data_location='./data.csv' ,Opt_flags=self.flags)
        
        for i in range(0,int(args.iterations)):
            print 'running iteration '+str(i+1)
            if self.runtime_limit>0:
                run_result = self.call_program(self.debs_command, limit=self.runtime_limit)
            else:
                print self.debs_command
                run_result = self.call_program(self.debs_command)
                print run_result
            
            temp_metric += (self.get_DEBS_benchmark(run_result['stdout']))
        
        return -1 * temp_metric/args.iterations # To maximize 
    
    def get_DEBS_benchmark(self,result):
        try:
            m=re.search( 'over all throughput \(events\/s\) :[0-9]*', result, flags=re.DOTALL)
            if m:
                query_1_throughput = m.group(0)
                query_1_throughput = int(re.sub('over all throughput \(events\/s\) :', '', query_1_throughput))
                return query_1_throughput 
            else:
                return 0
        except:
            return 0
        
        
if __name__ == '__main__':
    args = argparser.parse_args()
    debsTuner.main(args)
