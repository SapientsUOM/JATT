import argparse
import re

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
argparser.add_argument(
  '--jvm_spec_startup', default='java -jar SPECjvm2008.jar {source} -ikv -crf false --jvmArgs "{Opt_flags}"',
  help='command template to JVMSPEC2008 statup program tuning.. ')

argparser.add_argument(
  '--jvm_spec_nonstartup', default='java -jar SPECjvm2008.jar {source} -ikv -crf false -wt 30s -it 30s --jvmArgs "{Opt_flags}"',
  help='command template to JVMSPEC2008 nonstatup program tuning.. ')

argparser.add_argument('--spec_type', help='Select between startup and non_startup', default='startup')
class SpecJvmTuner(JvmFlagsTunerInterface):
    
    def __init__(self, *pargs, **kwargs):
        super(SpecJvmTuner, self).__init__(args, *pargs,
                                        **kwargs)
    
    def execute_program(self):
        temp_metric=0
        for i in range(0,int(args.iterations)):
            print 'running iteration '+str(i)
            if(args.spec_type == 'startup'):
                run_result = self.call_program(args.jvm_spec_startup.format(source=args.source,Opt_flags=self.flags))
            elif(args.spec_type == 'non_startup'):
                run_result = self.call_program(args.jvm_spec_nonstartup.format(source=args.source,Opt_flags=self.flags))
            temp_metric=temp_metric+self.get_ms_per_op_jvm(run_result['stdout'])
        temp_metric=float(temp_metric/int(args.iterations))
        return temp_metric
    
    def get_ms_per_op_jvm(self,result):
        m=re.search('Score on '+str(args.source)+': [0-9]*.[0-9]*|Score on '+str(args.source)+': [0-9]*',result,flags=re.DOTALL)
        ops_m=1
        if m:
            ops_m=m.group(0)
            ops_m =re.sub('Score on '+str(args.source)+': ','',ops_m)
            ops_m = re.sub(' ops/m','',ops_m)
        try:
            ops_m=float(ops_m)
        except:
            ops_m=1
    
        time_per_op=6000.0/ops_m
        return  time_per_op


if __name__ == '__main__':
    args = argparser.parse_args()
    SpecJvmTuner.main(args)