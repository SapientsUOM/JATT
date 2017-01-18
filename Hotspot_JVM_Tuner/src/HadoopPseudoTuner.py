import argparse
import re
import subprocess
import sys


import jvmtunerInterface
from jvmtunerInterface import JvmFlagsTunerInterface

argparser = argparse.ArgumentParser(parents=[jvmtunerInterface.argparser])
argparser.add_argument('--hadoop_run_command',
                       default='hadoop jar {hadoop_bench_jar} {source} {benchmark_paramerters}',
                       help='Command to run hadoop benchmark')
argparser.add_argument('--hadoop_bench_jar',help='hadoop benchmark jar file')
argparser.add_argument('--benchmark_paramerters', help='Parameters required to run Hadoop benchmark')
argparser.add_argument('--hadoop_node', help=
                       'Which node to tune, Possible Options: NameNode, DataNode, Client, DfsAll,ResourceManager, NodeManager')
argparser.add_argument('--hadoop_env_file')
argparser.add_argument('--yarn_env_file')

class HadoopPsedudoTuner(JvmFlagsTunerInterface):
    def __init__(self, args, *pargs, **kwargs):
        if(args.hadoop_node == 'NameNode'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR NAMENODE STARTED.*# OPENTUNER JVM SETTINGS FOR NAMENODE END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR NAMENODE STARTED\nHADOOP_NAMENODE_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR NAMENODE END'
            self.edit_file = args.hadoop_env_file
        elif(args.hadoop_node == 'DataNode'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR DATANODE STARTED.*# OPENTUNER JVM SETTINGS FOR DATANODE END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR DATANODE STARTED\nHADOOP_DATANODE_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR DATANODE END'
            self.edit_file = args.hadoop_env_file
        elif(args.hadoop_node == 'DfsAll'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR ALL STARTED.*# OPENTUNER JVM SETTINGS FOR ALL END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR ALL STARTED\nHADOOP_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR ALL END'
            self.edit_file = args.hadoop_env_file
        elif(args.hadoop_node == 'Client'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR CLIENT STARTED.*# OPENTUNER JVM SETTINGS FOR CLIENT END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR CLIENT STARTED\nHADOOP_CLIENT_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR CLIENT END'
            self.edit_file = args.hadoop_env_file
            
        elif(args.hadoop_node == 'ResourceManager'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER STARTED.*# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER STARTED\nYARN_RESOURCEMANAGER_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER END'
            self.edit_file = args.yarn_env_file
        elif(args.hadoop_node == 'NodeManager'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR NODEMANAGER STARTED.*# OPENTUNER JVM SETTINGS FOR NODEMANAGER END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR NODEMANAGER STARTED\nYARN_NODEMANAGER_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR NODEMANAGER END'
            self.edit_file = args.yarn_env_file
            
        self.benchmark = args.source
        self.run_command = args.hadoop_run_command.format(source=args.source,
                                                                            hadoop_bench_jar=args.hadoop_bench_jar,
                                                                            benchmark_paramerters=args.benchmark_paramerters)    
        super(HadoopPsedudoTuner, self).__init__(args, *pargs,
                                        **kwargs)
        
        
    def start_hadoop(self):
        dfs_start_output = self.cmd_execute('start-dfs.sh')
        print dfs_start_output['stdout']
        yarn_start_output = self.cmd_execute('start-yarn.sh')
        out = yarn_start_output['stdout']
        print out
        size = len(out.split('\n'))
        print size
        if(size > 4):
            raise Exception("Error Occurred")
        
    def stop_hadoop(self):
        dfs_stop_output = self.cmd_execute('stop-dfs.sh')
        print dfs_stop_output['stdout']
        yarn_stop_output = self.cmd_execute('stop-yarn.sh')
        print yarn_stop_output['stdout']
        
    def read_output(self,output):
        print output
        time = 0;
        if(self.benchmark == 'TestDFSIO'):
            m = re.search('Test exec time sec: (\d+.\d+)',output,flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        elif(self.benchmark == 'largesorter'):
            m = re.search('The job took (\d+) seconds', output, flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        elif(self.benchmark == 'pi'):
            m = re.search('Job Finished in (\d+.\d+) seconds',output, flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        elif(self.benchmark == 'mrbench'):
            m = re.search('AvgTime \(milliseconds\)(.*)',output,flags = re.DOTALL)
            print m.group(1)
            match = m.group(1)
            splits = match.split('\t')
            value = splits[len(splits)-1]
            print value
            time = int(value)
        elif(self.benchmark == 'terasort'):
            m = re.search('CPU time spent \(ms\)=(\d+)', output,flags = re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        return time
    
    def cmd_execute(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        p.wait()
        return {'stdout':out,
                'stderr':err}
    
    def execute_program(self):
        print self.run_command
        # Write jvm flags to configuration files 
        hadoop_file = open(self.edit_file,"r")
        file_content = hadoop_file.read()
        file_content = re.sub(self.match_string, self.subtitute_string1+'"'+self.flags+'"'+self.subtitute_string2, file_content,flags=re.DOTALL)
        hadoop_file.close()
        
        hadoop_file = open(self.edit_file,"w")
        hadoop_file.write(file_content)
        hadoop_file.close()
        
        run_time = 0;
        try:
            self.start_hadoop()
            self.cmd_execute('hdfs dfsadmin -safemode leave')
            
            #print 'First Run will be ignored'
            
            #first_run_out = self.cmd_execute(run_command)
            #print first_run_out['stderr']
            
            print 'Starting Benchmark for Tuning.........'
            
            for i in range(0,int(args.iterations)):
                run_result = self.cmd_execute(self.run_command)
                print 'run result stdout'
                print run_result['stdout']
                print 'run result error'
                print run_result['stderr']
                run_time += self.read_output(run_result['stderr'] + run_result['stdout'])
        except:
            print sys.exc_info()[0]
            run_time = 300000
        finally:
            self.cmd_execute('hdfs dfs -rmr /dfs/data/*')
            if(self.benchmark == 'terasort'):
                output = self.cmd_execute('hdfs dfs -rmr /dfs/cse/tera_out')
                print output['stdout']
                print output['stderr']
            self.stop_hadoop()
            
        return run_time/int(args.iterations)
        

if __name__ == '__main__':
    args = argparser.parse_args()
    HadoopPsedudoTuner.main(args)