'''
#Author:SapientS
#Date:25/10/2014
# This program contains the functionality to tune jvm flags to improve
# given java program performance
'''
import argparse
import sys

import jvmtunerInterface_GUI
from jvmtunerInterface_GUI import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface_GUI.argparser])
argparser.add_argument('--class_path',default='')
argparser.add_argument(
  '--bytecode_compile_template', default='javac {source}.java',
  help='command to compile to java byte code')
argparser.add_argument('--java_run_command', default='java -XX:ErrorFile=/dev/null -classpath {class_path} {flags} {source}')
class JavaProgramTuner(JvmFlagsTunerInterface):
    
    def __init__(self, *pargs, **kwargs):
        super(JavaProgramTuner, self).__init__(args, *pargs,
                                        **kwargs)
        
    def execute_program(self):
        temp_metric=0
        for i in range(0,int(args.iterations)):
            run_result = self.call_program(args.java_run_command.format(source=args.source,flags=self.flags,class_path=args.class_path))
            if run_result['stderr']:
				print 'Error:',run_result['stderr']
				return self.default_time*10
            else:
				#print 'std_out:',run_result['stdout']		
	    		temp_metric += run_result['time']
	    
        runtime = temp_metric/int(args.iterations) 
        return runtime
    
    def get_default_time(self):
        self.call_program(args.bytecode_compile_template.format(source=(args.class_path+args.source)))
        self.flags = ''
        self.default_time = self.execute_program()
        self.append_to_config_file('Default Configuration Metric:'+str(self.default_time))
        print >> sys.stderr,  ("Default Configuration Metric :%s" % str(self.default_time))
        
        return float(self.default_time)
            
if __name__ == '__main__':
    args = argparser.parse_args()
    JavaProgramTuner.main(args)
