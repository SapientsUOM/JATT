'''
#Author:SapientS
#Date:25/10/2014
# This program contains the functionality to tune jvm flags to improve
# given java program performance
'''

import adddeps
import datetime
import argparse
import opentuner
import logging
import os
import re
import sys
import subprocess
import pandas as pd
import common as cmn
import tomcathelper
import hadoopHelper

from opentuner.resultsdb.models import Result, TuningRun
from opentuner.search import manipulator
from numpy.f2py.diagnose import run_command

log = logging.getLogger('jvm_tuner')

argparser = argparse.ArgumentParser(parents=opentuner.argparsers())
argparser.add_argument('--source',
                       help='source file to compile (only give name e.g: MatrixMultiply)')
argparser.add_argument('--flags', default='bytecode,codecache,compilation,compiler,deoptimization,gc,interpreter,memory,priorities,temporary',
                       help='define flag combinations to feed separated by commas (E.g: gc,compiler)')
argparser.add_argument(
  '--bytecode-compile-template', default='javac {source}.java',
  help='command to compile to java byte code')
argparser.add_argument(
  '--jvm_spec_startup', default='java -jar SPECjvm2008.jar {source} -ikv -crf false --jvmArgs "{Opt_flags}"',
  help='command template to JVMSPEC2008 statup program tuning.. ')

argparser.add_argument(
  '--jvm_spec_nonstartup', default='java -jar SPECjvm2008.jar {source} -ikv -crf false -wt 30s -it 30s --jvmArgs "{Opt_flags}"',
  help='command template to JVMSPEC2008 nonstatup program tuning.. ')

argparser.add_argument(
  '--daCapo', default='java -jar {Opt_flags} dacapo-9.12-bach.jar {source}',
  help='command template to DaCapo benchmark Tuning.... ')

argparser.add_argument(
  '--tomcat', default='{source} Catalina.sh flag list: {Opt_flags}',
  help='command template to tomcat server benchmark Tuning.... ')


argparser.add_argument(
  '--TunerType', default='',
  help='To select the tuner type dacapo: to tune dacapo benchmark, spec_startup: to tune JVMSPEC2008, spec_non_sartup: to tune non startup of JVM SPEC, tomcat: to tune tomcat server..')

argparser.add_argument(
  '--warfilename', default='addrbook',
  help='To select the warfilename to run with tomcat. ')

argparser.add_argument(
  '--servlet', default='xmlservlet',
  help='To select the servlet to run with tomcat. ')

argparser.add_argument(
  '--requests', default='10000',
  help='number of requests to be processed ')

argparser.add_argument(
  '--ip', default='10.8.106.246',
  help='ip of the machine where tomcat is running ')

argparser.add_argument(
  '--username', default='cse',
  help='ssh username of the machine where tomcat is running ')

argparser.add_argument(
  '--password', default='cse@123',
  help='ssh password of the machine where tomcat is running ')

argparser.add_argument(
  '--benchmark_tool', default='ab',
  help='the benchmark tool to be used ')

argparser.add_argument('--hadoop_run_command',
                       default='hadoop jar {hadoop_bench_jar} {source} {benchmark_paramerters}',
                       help='Command to run hadoop benchmark')
argparser.add_argument('--hadoop_bench_jar',help='hadoop benchmark jar file')
argparser.add_argument('--benchmark_paramerters', help='Parameters required to run Hadoop benchmark')


class JvmFlagsTuner(opentuner.measurement.MeasurementInterface):
    
    def __init__(self, *pargs, **kwargs):
        super(JvmFlagsTuner, self).__init__(program_name=args.source, *pargs,
                                        **kwargs)
        
        self.flags_folder = 'Flags/'
        self.configuration_file_folder = 'Configurations/'
        self.tuner_config_file_folder='TunedConfiguration/'
        
        print 'JVM TUner Initializing...'
        datetime_now = datetime.datetime.now()
        print ("Tuner started on = %s" % datetime_now)
        self.append_to_config_file("JVM Hostspot Configuration file for benchmark %s" % args.source)
        self.append_to_config_file("Tuner started on = %s" % datetime_now)
        self.append_to_config_file("Tuning Flags : %s"% args.flags)
        self.default_metric=0 # Denotes the default metric value compared to measure tuning.
        self.improvement=0
        self.run_command_template=''
        self.tuner_type=''
        self.benchmark_tool=''
        self.flags=''
        self.default_metric=0
        self.runtime_limit=0;
        self.ignore_flags_list={'StackRedPages','StringTableSize'}
        
        
        self.choose_run_command_template()
        
        # First compile source to byte code
        #java_bytecode_compile = args.bytecode_compile_template.format(source=args.source)
        #subprocess.call(java_bytecode_compile,shell=True)     
        self.extract_jvm_flags()
        self.read_flag_dependancy_structure()
        
    '''Chooses the corresponding run command according to the tuner type.. '''
        
    def choose_run_command_template(self):
        self.tuner_type=args.TunerType
        if self.tuner_type=='dacapo':
            self.run_command_template=args.daCapo
            self.default_metric=self.execute_trget_program()
        elif self.tuner_type=='spec_startup':
            self.run_command_template=args.jvm_spec_startup
            self.default_metric=self.execute_trget_program()
        elif self.tuner_type=='spec_non_startup':
            self.run_command_template=args.jvm_spec_nonstartup
            self.default_metric=self.execute_trget_program()
        elif self.tuner_type=='tomcat':
            self.run_command_template=args.tomcat
            self.default_metric=self.execute_trget_program()
        elif self.tuner_type == 'hadoop':
            self.run_command_template = args.hadoop_run_command
            self.default_metric = self.execute_trget_program()
        
        self.runtime_limit=int(self.default_metric*1.5)
        print 'Default Configuration Metric:',str(self.default_metric)
        self.append_to_config_file('Default Configuration Metric:'+str(self.default_metric))
    
    def execute_trget_program(self):
        temp_metric=0
        if self.tuner_type=='spec_startup' or self.tuner_type=='spec_non_startup':
            for i in range(0,3):
                if self.runtime_limit>0:
                    run_result = self.call_program(self.run_command_template.format(source=args.source,Opt_flags=self.flags),limit=self.runtime_limit)
                else:
                    run_result = self.call_program(self.run_command_template.format(source=args.source,Opt_flags=self.flags))
                temp_metric=temp_metric+cmn.get_ms_per_op_jvm(run_result['stdout'], args)
            temp_metric=float(temp_metric/3)
            return temp_metric
        elif self.tuner_type=='dacapo':
            for i in range(0,3):
                #print self.runtime_limit
                if self.runtime_limit>0:
                    #print 'running with run time limit.. '
                    run_result = self.call_program(self.run_command_template.format(source=args.source,Opt_flags=self.flags),limit=self.runtime_limit)
                else:
                    run_result = self.call_program(self.run_command_template.format(source=args.source,Opt_flags=self.flags))
                temp_metric=temp_metric+cmn.get_ms_dacapo(run_result['stderr'], args)
            temp_metric=float(temp_metric/3)
            return temp_metric
        
        elif self.tuner_type=='tomcat':
            '''TOMCAT AB TOOL RUN CODE SHOULD COME HERE WITH ALL OF IT COMPHONENTS .......'''
            tomcat_helper = tomcathelper.TomcatHelper(args.warfilename, args.servlet, args.requests, args.ip, args.username, args.password)
            self.benchmark_tool = args.benchmark_tool
            temp_metric=float(tomcat_helper.run_command(self.flags,self.benchmark_tool))
            return temp_metric  
        
        elif self.tuner_type == 'hadoop':
            hadoop_helper = hadoopHelper.HadoopHelper()
            run_command = self.run_command_template.format(source=args.source,
                                                           hadoop_bench_jar=args.hadoop_bench_jar,
                                                           benchmark_paramerters=args.benchmark_paramerters)
            temp_metric = hadoop_helper.run_hadoop_benchmark(run_command, args.source, self.flags) 
            return temp_metric     
    
    def extract_jvm_flags(self):
        """
        Print all flags and their corresponding values (including
        erogonomically changed flags) and write to flags.csv  
        """
        if(not(os.path.isfile(self.configuration_file_folder+'flags.csv'))):
            subprocess.call("java -XX:+PrintFlagsFinal >"+ self.configuration_file_folder+"flags.txt", shell=True)
            f = open(self.configuration_file_folder+"flags.txt", "r");
            flags = f.read()
            flags = re.sub('\[.*?\]','',flags )
            flags = re.sub('{.*?}','',flags)
            flags = re.sub(':* *=','',flags)
            flags = re.sub(' *\n *', '\n', flags)
            flags = re.sub(' +', ',', flags)
            if flags[0] == '\n':
                flags = 'type,flagname,default' + flags[0:]
            else:
                flags = 'type,flagname,default\n' + flags[0:]
        
            f = open(self.configuration_file_folder+"flags.csv", "w");
            f.write(flags)
            f.close()
        
        flags = pd.read_csv(self.configuration_file_folder+'flags.csv')
        for r in self.ignore_flags_list:
            flags=flags[flags.flagname!=r]
        
        
        """
        Separate in to boolean and parameter flags
        """            
        self.all_bool_flags = flags[flags.type == 'bool']
        self.all_bool_flags.to_csv(self.configuration_file_folder+'jvm_bool_flags.csv',index=False)
        
        flags= flags[flags.type != 'bool']
        flags = flags[flags.type != 'ccstrlist']
        flags = flags[flags.type != 'ccstr']
        self.all_param_flags = flags
        self.all_param_flags.default = self.all_param_flags.default.apply(cmn.convert_to_numeric)
        self.all_param_flags['min'] = self.all_param_flags.default.apply(cmn.get_min)
        self.all_param_flags['max'] = self.all_param_flags.default.apply(cmn.get_max)
        self.all_param_flags.to_csv(self.configuration_file_folder+'jvm_param_flags.csv', index=False)
        
    """
        Flag Structure is important in reducing wrong combinations
        and unnecessary flag combinations
    """    
    def read_flag_dependancy_structure(self):
        """
            We have defined 10 main flag categories given in java source code 
            globals.hpp file
            categories
            -------------------------------------
            bytecode, codecache, compilation, compiler, deoptimization
            gc, interpreter, memory, priorities, temporary
        """
        self.bytecode=False
        self.codecache = False
        self.compilation = False
        self.compiler = False
        self.deoptimization = False
        self.gc = False 
        self.interpreter = False
        self.memory = False 
        self.priorities = False
        self.temporary = False
        
        flag_types = args.flags.split(',')
        self.bool_flags = []
        self.param_flags = []
        for flag_type in flag_types:
            if flag_type == 'bytecode':
                self.bytecode = True
                self.bytecode_bool, self.bytecode_param = self.prepare_flags(self.flags_folder+'ByteCode/bytecode.csv')
                self.bool_flags.append(self.bytecode_bool)
                self.param_flags.append(self.bytecode_param)
                
            elif flag_type == 'codecache':
                self.codecache = True
                self.codecache_bool, self.codecache_param = self.prepare_flags(self.flags_folder+'CodeCache/code_cache.csv')
                self.bool_flags.append(self.codecache_bool)
                self.param_flags.append(self.codecache_param)
                
            elif flag_type == 'compilation':
                """
                    Compilation has two files. flags in tieredCompilation only valid
                    if in compilation tieredcompilation == true 
                """
                self.compilation = True
                self.compilation_bool, self.compilation_param = self.prepare_flags(self.flags_folder+'Compilation/compilation.csv')
                self.bool_flags.append(self.compilation_bool)
                self.param_flags.append(self.compilation_param)
                
                self.tiered_compilation_bool, self.tiered_compilation_param = self.prepare_flags(self.flags_folder+'Compilation/tieredCompilation.csv')
                self.bool_flags.append(self.tiered_compilation_bool)
                self.param_flags.append(self.tiered_compilation_param)
                
            elif flag_type == 'compiler':
                """
                    C1 - Client Compiler (In 64bit version only used with tiered compilation)
                    C2 - Server Compiler
                """
                self.compiler = True
                self.client_bool, self.client_param = self.prepare_flags(self.flags_folder+'Compiler/c1_compiler.csv')
                self.bool_flags.append(self.client_bool)
                self.param_flags.append(self.client_param)   
                
                self.server_bool, self.server_param = self.prepare_flags(self.flags_folder+'Compiler/c2_compiler.csv')
                self.bool_flags.append(self.server_bool)
                self.param_flags.append(self.server_param)       
                
                self.compiler_common_bool, self.compiler_common_param = self.prepare_flags(self.flags_folder+'Compiler/compiler_common.csv')
                self.bool_flags.append(self.compiler_common_bool)
                self.param_flags.append(self.compiler_common_param)                           
                
            elif flag_type == 'deoptimization':
                self.deoptimization = True
                self.deoptimization_bool, self.deoptimization_param = self.prepare_flags(self.flags_folder+'DeOptimization/deoptimization.csv')
                self.bool_flags.append(self.deoptimization_bool)
                self.param_flags.append(self.deoptimization_param)
                
            elif flag_type == 'gc':
                self.gc = True
                self.gc_select_flags = pd.read_csv(self.flags_folder+'GC/gc_select.csv').flagname 
                self.bool_flags.append(self.gc_select_flags)
                
                # common gc means flags used by the serial collector
                self.gc_common_bool, self.gc_common_param = self.prepare_flags(self.flags_folder+'GC/gc_common.csv')
                self.bool_flags.append(self.gc_common_bool)
                self.param_flags.append(self.gc_common_param)                
                
                # throughput collector flags
                self.parallel_common_bool, self.parallel_common_param = self.prepare_flags(self.flags_folder+'GC/parallel_common.csv')
                self.bool_flags.append(self.parallel_common_bool)
                self.param_flags.append(self.parallel_common_param)
                
                self.parallel_young_bool, self.parallel_young_param = self.prepare_flags(self.flags_folder+'GC/parallel.csv')
                self.bool_flags.append(self.parallel_young_bool)
                self.param_flags.append(self.parallel_young_param)    
                
                self.parallel_old_bool, self.parallel_old_param = self.prepare_flags(self.flags_folder+'GC/parallelold.csv')
                self.bool_flags.append(self.parallel_old_bool)
                self.param_flags.append(self.parallel_old_param)
                
                # cms collector flags
                self.cms_bool, self.cms_param = self.prepare_flags(self.flags_folder+'GC/cms_collector.csv')
                self.bool_flags.append(self.cms_bool)
                self.param_flags.append(self.cms_param)
                
                self.parnew_bool, self.parnew_param = self.prepare_flags(self.flags_folder+'GC/parnew.csv')
                self.bool_flags.append(self.parnew_bool)
                self.param_flags.append(self.parnew_param)    
                
                # G1 collector flags
                self.g1_bool, self.g1_param = self.prepare_flags(self.flags_folder+'GC/g1_globals.csv')
                self.bool_flags.append(self.g1_bool)
                self.param_flags.append(self.g1_param)
            elif flag_type == 'interpreter':
                self.interpreter=True
                self.interpreter_bool,self.interpreter_param = self.prepare_flags(self.flags_folder+'Interpreter/interpreter.csv')
                self.bool_flags.append(self.interpreter_bool)
                self.param_flags.append(self.interpreter_param)
            elif flag_type == 'memory':
                self.memory=True
                self.memory_bool,self.memory_param = self.prepare_flags(self.flags_folder+'Memory/memory.csv')
                self.bool_flags.append(self.memory_bool)
                self.param_flags.append(self.memory_param)
            elif flag_type == 'priorities':
                self.priorities=True
                self.priorities_bool,self.priorities_param = self.prepare_flags(self.flags_folder+'Priorities/priorities.csv')
                self.bool_flags.append(self.priorities_bool)
                self.param_flags.append(self.priorities_param)
            elif flag_type == 'temporary':
                self.temporary=True
                self.temporary_bool,self.temporary_param = self.prepare_flags(self.flags_folder+'Temporary/temporary.csv')
                self.bool_flags.append(self.temporary_bool)
                self.param_flags.append(self.temporary_param)
        
        
    def prepare_flags(self,filename):
        temp = pd.read_csv(filename)
        bool_out = (pd.merge(temp,self.all_bool_flags,on='flagname')).flagname
        
        param_out = dict()
        df = pd.merge(temp,self.all_param_flags,on='flagname')
        for index,row in df.iterrows():
            param_out[index] = {'flagname': row['flagname'],
                                        'min': row['min'],
                                        'max': row['max']}
        return bool_out,param_out
    

    def append_to_config_file(self,text):
        with open(self.tuner_config_file_folder+'/'+args.source, "a") as config_file:
            config_file.write(text+'\n')
            
              
    def manipulator(self):
        m = manipulator.ConfigurationManipulator()
        for flag_set in self.bool_flags:
            for flag in flag_set:
                m.add_parameter(manipulator.EnumParameter(flag, ['on', 'off']))
        for flag_set in self.param_flags:
            for flag in flag_set:
                value = flag_set[flag]
                if(value['min'] >= value['max']):
                    m.add_parameter(manipulator.IntegerParameter(value['flagname'],value['max'],value['min']))
                else:
                    m.add_parameter(manipulator.IntegerParameter(value['flagname'],value['min'],value['max']))
        return m
    
    def add_to_flags_bool(self,cfg,flag):
        if cfg[flag] == 'on':
            self.flags += ' -XX:+{0}'.format(flag)
        elif cfg[flag] == 'off':
            self.flags += ' -XX:-{0}'.format(flag)
           
    def add_to_flags_param(self,cfg,flag,flag_type):
        value = flag_type[flag]
        param_flag = value['flagname']
        self.flags += ' -XX:'+param_flag+"="+str(cfg[param_flag])

    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        self.flags = ''
        
        cfg = desired_result.configuration.data
        self.flags = ''
        # assign garbage collector flags
        for flag in self.gc_select_flags:
            self.add_to_flags_bool(cfg,flag)
            
        for gc_flag in self.g1_bool:
            self.add_to_flags_bool(cfg, gc_flag)
        for gc_flag in self.g1_param:
            self.add_to_flags_param(cfg, gc_flag, self.g1_param)
            
        for gc_flag in self.parallel_common_bool:
            self.add_to_flags_bool(cfg, gc_flag)
        for gc_flag in self.parallel_common_param:
            self.add_to_flags_param(cfg, gc_flag, self.parallel_common_param)
                        
        for gc_flag in self.parallel_young_bool:
            self.add_to_flags_bool(cfg, gc_flag)
        for gc_flag in self.parallel_young_param:
            self.add_to_flags_param(cfg, gc_flag, self.parallel_young_param)
                        
        for parallel_old_flag in self.parallel_old_bool:
            self.add_to_flags_bool(cfg, parallel_old_flag)
        for parallel_old_flag in self.parallel_old_param:
            self.add_to_flags_param(cfg, parallel_old_flag, self.parallel_old_param)
                                
        for gc_flag in self.cms_bool:
            self.add_to_flags_bool(cfg, gc_flag)
        for gc_flag in self.cms_param:
            self.add_to_flags_param(cfg, gc_flag, self.cms_param)
      
        for parnew_flag in self.parnew_bool:
            self.add_to_flags_bool(cfg, parnew_flag)
        for parnew_flag in self.parnew_param:
            self.add_to_flags_param(cfg, parnew_flag, self.parnew_param)
            
        #add common gc flags
        for gc_flag in self.gc_common_bool:
            self.add_to_flags_bool(cfg, gc_flag)
        for gc_flag in self.gc_common_param:
            self.add_to_flags_param(cfg, gc_flag, self.gc_common_param)


        for flag in self.compilation_bool:
            self.add_to_flags_bool(cfg,flag)
        for flag in self.compilation_param:
            self.add_to_flags_param(cfg, flag, self.compilation_param)


        # use tiered compilation flags
        for tiered_flag in self.tiered_compilation_bool:
            self.add_to_flags_bool(cfg, tiered_flag)
        for tiered_flag in self.tiered_compilation_param:
            self.add_to_flags_param(cfg, tiered_flag, self.tiered_compilation_param)
  
        for c1_flag in self.client_bool:
            self.add_to_flags_bool(cfg, c1_flag)                  
        for c1_flag in self.client_param:
            self.add_to_flags_param(cfg, c1_flag, self.client_param)

        for flag in self.compiler_common_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.compiler_common_param:
            self.add_to_flags_param(cfg, flag, self.compiler_common_param)                   
                    
        for flag in self.server_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.server_param:
            self.add_to_flags_param(cfg, flag, self.server_param)
            
        for flag in self.bytecode_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.bytecode_param: 
            self.add_to_flags_param(cfg, flag, self.bytecode_param)
            
        for flag in self.codecache_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.codecache_param:
            self.add_to_flags_param(cfg, flag, self.codecache_param)

        for flag in self.deoptimization_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.deoptimization_param:
            self.add_to_flags_param(cfg, flag, self.deoptimization_param)     
            
        for flag in self.interpreter_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.interpreter_param:
            self.add_to_flags_param(cfg, flag,self.interpreter_param)
            
        for flag in self.memory_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.memory_param:
            self.add_to_flags_param(cfg, flag,self.memory_param )
            
        for flag in self.priorities_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.priorities_param:
            self.add_to_flags_param(cfg, flag,self.priorities_param )
            
        for flag in self.temporary_bool:
            self.add_to_flags_bool(cfg, flag)
        for flag in self.temporary_param:
            self.add_to_flags_param(cfg, flag,self.temporary_param )        
        #print self.flags
        run_time=self.execute_trget_program()
        temp_improvement=float((self.default_metric-run_time)/self.default_metric)
        if temp_improvement>= self.improvement:
            self.improvement=temp_improvement
            if(args.TunerType == 'hadoop'):
                self.append_to_config_file(self.run_command_template.format(source=args.source,
                                                                            hadoop_bench_jar=args.hadoop_bench_jar,
                                                                            benchmark_paramerters=args.benchmark_paramerters))
                self.append_to_config_file(args.flags)
                self.append_to_config_file(self.flags)
            else:
                self.append_to_config_file(self.run_command_template.format(source=args.source,Opt_flags=self.flags))
            self.append_to_config_file("Improvement: %s" %self.improvement)
            self.append_to_config_file("Configuration Found At: %s" %datetime.datetime.now())
            
       
        return Result(time=run_time)
            
if __name__ == '__main__':
    opentuner.init_logging()
    args = argparser.parse_args()
    JvmFlagsTuner.main(args)
