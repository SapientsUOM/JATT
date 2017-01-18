'''
#Author:SapientS
#Date:25/10/2014
# This program contains the functionality to tune jvm flags to improve
# given java program performance
'''
import argparse

import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
argparser.add_argument(
  '--bytecode_compile_template', default='javac {source}.java',
  help='command to compile to java byte code')
argparser.add_argument('--java_run_command', default='java {flags} {source}')
class JavaProgramTuner(JvmFlagsTunerInterface):
   # global count
    #count = 0

    def __init__(self, *pargs, **kwargs):
        super(JavaProgramTuner, self).__init__(args, *pargs,
                                        **kwargs)

    def execute_program(self):
       temp_metric=0
        for i in range(0,int(args.iterations)):
            run_result = self.call_program(args.java_run_command.format(source=args.source,flags=self.flags),60)
           
            if run_result['stderr']:
                print 'Error std err:',run_result['stderr']
                return self.default_time*10
            elif self.initialization_error in run_result['stdout']:
                print 'Error in stdout 1:',run_result['stdout']
                return self.default_time*10
            elif self.shared_space_error in run_result['stdout']:
                print 'Error in stdout 2:',run_result['stdout']
                return self.default_time*10
            elif self.warning_error in run_result['stdout']:
                print 'Error in std_out 3: ',run_result['stdout']
                return self.default_metric*10
            else:
                temp_metric += run_result['time']
        runtime = temp_metric/int(args.iterations)
        return runtime
    
    def get_default_time(self):
        self.call_program(args.bytecode_compile_template.format(source=args.source))
        self.flags = ''
	print (args.java_run_command.format(source=args.source,flags=self.flags))
        self.default_time = self.execute_program()
        print 'Default Configuration Metric:',str(self.default_time)

        self.append_to_config_file('Default Configuration Metric:'+str(self.default_time))
        return float(self.default_time)
            
if __name__ == '__main__':
    args = argparser.parse_args()
    JavaProgramTuner.main(args)
