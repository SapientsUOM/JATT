import xml.etree.ElementTree as ET
import subprocess
import re
import sys

class HadoopHelper():
    
    def __init__(self):
        self.mapred_file = '/home/chalitha/my_folder/apache_dev/Hadoop/hadoop-pseudo/etc/hadoop/mapred-site.xml'
    
    def start_hadoop(self):
        dfs_start_output = self.call_program('start-dfs.sh')
        print dfs_start_output['stdout']
        yarn_start_output = self.call_program('start-yarn.sh')
        print yarn_start_output['stdout']
        
    def stop_hadoop(self):
        dfs_stop_output = self.call_program('stop-dfs.sh')
        print dfs_stop_output['stdout']
        yarn_stop_output = self.call_program('stop-yarn.sh')
        print yarn_stop_output['stdout']
        
    def read_output(self,benchmark,output):
        print output
        time = 0;
        if(benchmark == 'TestDFSIO'):
            m = re.search('Test exec time sec: (\d+.\d+)',output,flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        elif(benchmark == 'largesorter'):
            m = re.search('The job took (\d+) seconds', output, flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        return time
        
    def run_hadoop_benchmark(self,run_command,benchmark,flags):
        print run_command
        # Write jvm flags to configuration file
        tree = ET.parse(self.mapred_file)
        root = tree.getroot()
        root[1][1].text = flags;
        tree.write(self.mapred_file)
        
        self.start_hadoop()
        self.call_program('hdfs dfsadmin -safemode leave')
        
        run_time = 0;
        try:
            print 'First Run will be ignored'
            
            first_run_out = self.call_program(run_command)
            print first_run_out['stderr']
            
            print 'Starting Benchmark for Tuning.........'
            
            for i in range(0,2):
                run_result = self.call_program(run_command)
                print 'run result stdout'
                print run_result['stdout']
                print 'run result error'
                print run_result['stderr']
                run_time += self.read_output(benchmark, run_result['stderr'] + run_result['stdout'])
        except:
            print sys.exc_info()[0]
            run_time = 30000
        finally:
            self.stop_hadoop()
            self.call_program('rm -r /home/cse/SapientS/hadoop-pseudo/hadoop-temp/dfs/data')
        
        return run_time/2
    
    def call_program(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        p.wait()
        return {'stdout':out,
                'stderr':err}
        
        
