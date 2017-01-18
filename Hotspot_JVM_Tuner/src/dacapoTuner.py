import argparse
import re

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
argparser.add_argument(
  '--daCapo', default='java -jar {Opt_flags} dacapo-9.12-bach.jar {source}',
  help='command template to DaCapo benchmark Tuning.... ')

class DaCapoTuner(JvmFlagsTunerInterface):
    
    def __init__(self, *pargs, **kwargs):
        super(DaCapoTuner, self).__init__(args, *pargs,
                                        **kwargs)
        
    def execute_program(self):
        temp_metric = 0
        for i in range(0,int(args.iterations)):
            print 'running iteration '+str(i+1)
            if self.runtime_limit>0:
                run_result = self.call_program(args.daCapo.format(source=args.source,Opt_flags=self.flags),limit=self.runtime_limit)
            else:
                run_result = self.call_program(args.daCapo.format(source=args.source,Opt_flags=self.flags))
            temp_metric += self.get_ms_dacapo(run_result['stderr'])
        temp_metric=float(temp_metric/int(args.iterations))
        return temp_metric
    
    def get_ms_dacapo(self,result):
        m=re.search('===== DaCapo 9.12 '+str(args.source)+' PASSED in [0-9]* msec', result, flags=re.DOTALL)
        m_sec=10000000
        if m:
            m_sec=m.group(0)
            m_sec=re.sub('===== DaCapo 9.12 '+str(args.source)+' PASSED in ', '',m_sec)
            m_sec=re.sub(' msec','',m_sec)
            m_sec=int(m_sec)
        return m_sec
        
if __name__ == '__main__':
    args = argparser.parse_args()
    DaCapoTuner.main(args)