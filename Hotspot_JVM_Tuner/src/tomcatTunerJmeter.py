import re
import sys
import subprocess
import argparse

import tomcatTunerInterface
from tomcatTunerInterface import TomcatTunerAbstract

argparser = argparse.ArgumentParser(parents=[tomcatTunerInterface.argparser])

class TomcatTunerJmeter(TomcatTunerAbstract):

    def __init__(self, *pargs, **kwargs):
        self.jmeter_command = 'java -jar apps/apache_jmeter/bin/ApacheJMeter.jar -n -t apps/apache_jmeter/bin/examples/PerformanceTestPlanMemoryThread_500_1_1.jmx > apps/apache_jmeter/bin/jmeter_result.txt'
        super(TomcatTunerJmeter, self).__init__(args, *pargs,
                                        **kwargs)


    def run_benchmark(self):
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

if __name__ == '__main__':
    args = argparser.parse_args()
    TomcatTunerJmeter.main(args)