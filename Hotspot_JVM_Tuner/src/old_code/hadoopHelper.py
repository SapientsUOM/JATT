import subprocess
import re
import sys

class HadoopHelper():
    
    def __init__(self, hadoop_node):
        hadoop_env_file = '/home/chalitha/my_folder/apache_dev/Hadoop/hadoop-pseudo/etc/hadoop/hadoop-env.sh'
        yarn_file = '/home/chalitha/my_folder/apache_dev/Hadoop/hadoop-pseudo/etc/hadoop/yarn-env.sh'
        
        if(hadoop_node == 'NameNode'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR NAMENODE STARTED.*# OPENTUNER JVM SETTINGS FOR NAMENODE END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR NAMENODE STARTED\nHADOOP_NAMENODE_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR NAMENODE END'
            self.edit_file = hadoop_env_file
        elif(hadoop_node == 'DataNode'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR DATANODE STARTED.*# OPENTUNER JVM SETTINGS FOR DATANODE END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR DATANODE STARTED\nHADOOP_DATANODE_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR DATANODE END'
            self.edit_file = hadoop_env_file
        elif(hadoop_node == 'DfsAll'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR ALL STARTED.*# OPENTUNER JVM SETTINGS FOR ALL END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR ALL STARTED\nHADOOP_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR ALL END'
            self.edit_file = hadoop_env_file
        elif(hadoop_node == 'Client'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR CLIENT STARTED.*# OPENTUNER JVM SETTINGS FOR CLIENT END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR CLIENT STARTED\nHADOOP_CLIENT_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR CLIENT END'
            self.edit_file = hadoop_env_file
            
        elif(hadoop_node == 'ResourceManager'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER STARTED.*# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER STARTED\nYARN_RESOURCEMANAGER_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR RESOURCEMANAGER END'
            self.edit_file = yarn_file
        elif(hadoop_node == 'NodeManager'):
            self.match_string = '# OPENTUNER JVM SETTINGS FOR NODEMANAGER STARTED.*# OPENTUNER JVM SETTINGS FOR NODEMANAGER END'
            self.subtitute_string1 = '# OPENTUNER JVM SETTINGS FOR NODEMANAGER STARTED\nYARN_NODEMANAGER_OPTS='
            self.subtitute_string2 = '\n# OPENTUNER JVM SETTINGS FOR NODEMANAGER END'
            self.edit_file = yarn_file
            
    
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
        elif(benchmark == 'pi'):
            m = re.search('Job Finished in (\d+.\d+) seconds',output, flags=re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        elif(benchmark == 'mrbench'):
            m = re.search('AvgTime \(milliseconds\)(.*)',output,flags = re.DOTALL)
            print m.group(1)
            match = m.group(1)
            splits = match.split('\t')
            value = splits[len(splits)-1]
            print value
            time = int(value)
        elif(benchmark == 'terasort'):
            m = re.search('CPU time spent \(ms\)=(\d+)', output,flags = re.DOTALL)
            print m.group(1)
            time = float(m.group(1))
        return time
        
    def run_hadoop_benchmark(self,run_command,benchmark,flags):
        print run_command
        # Write jvm flags to configuration files 
        hadoop_file = open(self.edit_file,"r")
        file_content = hadoop_file.read()
        file_content = re.sub(self.match_string, self.subtitute_string1+'"'+flags+'"'+self.subtitute_string2, file_content,flags=re.DOTALL)
        hadoop_file.close()
        
        hadoop_file = open(self.edit_file,"w")
        hadoop_file.write(file_content)
        hadoop_file.close()
        
        run_time = 0;
        try:
            self.start_hadoop()
            self.cmd_execute('hdfs dfsadmin -safemode leave')
            
            print 'First Run will be ignored'
            
            #first_run_out = self.cmd_execute(run_command)
            #print first_run_out['stderr']
            
            print 'Starting Benchmark for Tuning.........'
            
            for i in range(0,1):
                run_result = self.cmd_execute(run_command)
                print 'run result stdout'
                print run_result['stdout']
                print 'run result error'
                print run_result['stderr']
                run_time += self.read_output(benchmark, run_result['stderr'] + run_result['stdout'])
        except:
            print sys.exc_info()[0]
            run_time = 20000
        finally:
            self.cmd_execute('hdfs dfs -rmr /dfs/data/*')
            if(benchmark == 'terasort'):
                output = self.cmd_execute('hdfs dfs -rmr /dfs/cse/tera_out')
                print output['stdout']
                print output['stderr']
            self.stop_hadoop()
            
        return run_time/2
    
    def cmd_execute(self, command):
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        p.wait()
        return {'stdout':out,
                'stderr':err}
        
        
