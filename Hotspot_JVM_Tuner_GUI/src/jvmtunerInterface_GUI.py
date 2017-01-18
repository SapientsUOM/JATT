'''
#Author:SapientS
#Date:25/10/2014
# This program contains the functionality to tune jvm flags to improve
# given java program performance
'''
import abc
import adddeps
import datetime
import argparse
import opentuner
import logging
import os
import re
import subprocess
import pandas as pd
import common as cmn
import sys

from opentuner.resultsdb.models import Result, TuningRun
from opentuner.search import manipulator
from numpy.f2py.diagnose import run_command



argparser = argparse.ArgumentParser(parents=opentuner.argparsers(),add_help=False)
argparser.add_argument('--configfile',
                       help='file to write down the configurations')
argparser.add_argument('--source',
                       help='source file to compile (only give name e.g: MatrixMultiply)')
argparser.add_argument('--flags', default='bytecode,codecache,compilation,compiler,deoptimization,gc,interpreter,memory,priorities,temporary',
                       help='define flag combinations to feed separated by commas (E.g: gc,compiler)')
argparser.add_argument('--iterations',
                       help='number of iterations to run a program to average runtime',
                       default='3')
argparser.add_argument('--runtimefraction',
                       help='how much time as the default time should the tuner wait for a tuning configuration to work',
                       default='1.5')
class JvmFlagsTunerInterface(opentuner.measurement.MeasurementInterface):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, args, *pargs, **kwargs):
        super(JvmFlagsTunerInterface, self).__init__(program_name=args.source, *pargs,
                                        **kwargs)
        self.args = args
        self.configfile = self.args.configfile
        self.current_location = os.path.dirname(os.path.abspath(__file__))
        self.flags_folder = self.current_location+'/Flags/'
        self.configuration_file_folder = self.current_location+'/Configurations/'
        self.tuner_config_file_folder=self.current_location+'/TunedConfiguration/'
        if not os.path.exists(self.configuration_file_folder):
            os.makedirs(self.configuration_file_folder)
        
        print >> sys.stderr,  'JVM TUner Initializing...'
        datetime_now = datetime.datetime.now()
        print >> sys.stderr,  ("Tuner started on = %s" % datetime_now)
        self.append_to_config_file("JVM Hostspot Configuration file for benchmark %s" % args.source)
        self.append_to_config_file("Tuner started on = %s" % datetime_now)
        self.append_to_config_file("Tuning Flags : %s"% args.flags)
        self.improvement=0
        self.runtime_limit=0
        self.default_metric= self.get_default_time() # Denotes the default metric value compared to measure tuning.
        self.ignore_flags_list={'StackRedPages','StringTableSize'}
                
        # First compile source to byte code
        #java_bytecode_compile = args.bytecode_compile_template.format(source=args.source)
        #subprocess.call(java_bytecode_compile,shell=True)     
        self.extract_jvm_flags()
        self.read_flag_dependancy_structure()
        
    
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
        
        flag_types = self.args.flags.split(',')
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
#         with open(self.args.configfile, "a") as config_file:
#             config_file.write(text+'\n')
        if self.configfile != "":
            with open(self.configfile, "a") as config_file:
                config_file.write(text+'\n')
		config_file.close()
            
        
#        Substring self.args.source to get the file name and write it to the folder
        
        else:
            sourcefile = self.args.source
            if "/" in sourcefile:
                words_in_folder = sourcefile.split("/")
                sourcefile = words_in_folder[len(words_in_folder)-1]
            if "." in sourcefile:
                sourcefile = sourcefile.split(".")[0]
            with open(self.tuner_config_file_folder+'/'+sourcefile, "a") as config_file:
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
        
        # assign garbage collector flags
        if(self.gc):
            for flag in self.gc_select_flags:
                if cfg[flag] == 'on':
                    self.flags += ' -XX:+{0}'.format(flag)
                    # if serial gc only the common gc flags will be used
                    if flag == 'UseSerialGC':
                        break
                    # if g1 gc only use g1 related flags + common
                    elif flag == 'UseG1GC':
                        for gc_flag in self.g1_bool:
                            self.add_to_flags_bool(cfg, gc_flag)
                        for gc_flag in self.g1_param:
                            self.add_to_flags_param(cfg, gc_flag, self.g1_param)
                        break
                    elif flag == 'UseParallelGC':
                        for gc_flag in self.parallel_common_bool:
                            self.add_to_flags_bool(cfg, gc_flag)
                        for gc_flag in self.parallel_common_param:
                            self.add_to_flags_param(cfg, gc_flag, self.parallel_common_param)
                        
                        for gc_flag in self.parallel_young_bool:
                            self.add_to_flags_bool(cfg, gc_flag)
                        for gc_flag in self.parallel_young_param:
                            self.add_to_flags_param(cfg, gc_flag, self.parallel_young_param)
                        
                        # with parallel gc it is possible to use or not to use parallel old    
                        for gc_flag in self.gc_select_flags:
                            if gc_flag == 'UseParallelOldGC':
                                if cfg[gc_flag] == 'on':
                                    self.flags += ' -XX:+{0}'.format(gc_flag)
                                    for parallel_old_flag in self.parallel_old_bool:
                                        self.add_to_flags_bool(cfg, parallel_old_flag)
                                    for parallel_old_flag in self.parallel_old_param:
                                        self.add_to_flags_param(cfg, parallel_old_flag, self.parallel_old_param)
                                elif cfg[gc_flag] == 'off':
                                    self.flags += ' -XX:-{0}'.format(gc_flag)
                        break
                                    
                    elif flag == 'UseParallelOldGC':
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
                        break
                    
                    elif flag == 'UseConcMarkSweepGC':
                        for gc_flag in self.cms_bool:
                            self.add_to_flags_bool(cfg, gc_flag)
                        for gc_flag in self.cms_param:
                            self.add_to_flags_param(cfg, gc_flag, self.cms_param)
                            
                        for gc_flag in self.gc_select_flags:
                            if gc_flag == 'UseParNewGC':
                                if cfg[gc_flag] == 'on':
                                    self.flags += ' -XX:+{0}'.format(gc_flag)
                                    for parnew_flag in self.parnew_bool:
                                        self.add_to_flags_bool(cfg, parnew_flag)
                                    for parnew_flag in self.parnew_param:
                                        self.add_to_flags_param(cfg, parnew_flag, self.parnew_param)
                                elif cfg[gc_flag] == 'off':
                                    self.flags += ' -XX:-{0}'.format(gc_flag)
                        break
                    
                    elif flag == 'UseParNewGC':
                        for gc_flag in self.parnew_bool:
                            self.add_to_flags_bool(cfg, gc_flag)
                        for gc_flag in self.parnew_param:
                            self.add_to_flags_param(cfg, gc_flag, self.parnew_param)
                            
                        for gc_flag in self.gc_select_flags:
                            if gc_flag == 'UseConcMarkSweepGC':
                                if cfg[gc_flag] == 'on':
                                    self.flags += ' -XX:+{0}'.format(gc_flag)
                                    for cms_flag in self.cms_bool:
                                        self.add_to_flags_bool(cfg, cms_flag)
                                    for cms_flag in self.cms_param:
                                        self.add_to_flags_param(cfg, cms_flag, self.cms_param)
                                elif cfg[gc_flag] == 'off':
                                    self.flags += ' -XX:-{0}'.format(gc_flag)
                        break
                    
            #add common gc flags
            for gc_flag in self.gc_common_bool:
                self.add_to_flags_bool(cfg, gc_flag)
            for gc_flag in self.gc_common_param:
                self.add_to_flags_param(cfg, gc_flag, self.gc_common_param)

                            
        # assign compilation flags
        if(self.compilation):
            for flag in self.compilation_bool:
                if cfg[flag] == 'on':
                    self.flags += ' -XX:+{0}'.format(flag)
                    # if tieredCompilation is on use tiered compilation + c1 compiler flags
                    if flag == 'TieredCompilation':
                        # use tiered compilation flags
                        for tiered_flag in self.tiered_compilation_bool:
                            self.add_to_flags_bool(cfg, tiered_flag)
                        for tiered_flag in self.tiered_compilation_param:
                            self.add_to_flags_param(cfg, tiered_flag, self.tiered_compilation_param)
                        
                        # if compiler flags are used use client compiler flags
                        if(self.compiler):
                            for c1_flag in self.client_bool:
                                self.add_to_flags_bool(cfg, c1_flag)
                                    
                            for c1_flag in self.client_param:
                                self.add_to_flags_param(cfg, c1_flag, self.client_param)
                                
                elif cfg[flag] == 'off':
                    self.flags += ' -XX:-{0}'.format(flag)
                    
            for flag in self.compilation_param:
                self.add_to_flags_param(cfg, flag, self.compilation_param)
                
        # assign Compiler flags
        if(self.compiler):
            for flag in self.compiler_common_bool:
                self.add_to_flags_bool(cfg, flag)
                    
            for flag in self.compiler_common_param:
                self.add_to_flags_param(cfg, flag, self.compiler_common_param)                   
                    
            for flag in self.server_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.server_param:
                self.add_to_flags_param(cfg, flag, self.server_param)
    
        if(self.bytecode):
            for flag in self.bytecode_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.bytecode_param:
                self.add_to_flags_param(cfg, flag, self.bytecode_param)
                
        if(self.codecache):
            for flag in self.codecache_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.codecache_param:
                self.add_to_flags_param(cfg, flag, self.codecache_param)
                
        if(self.deoptimization):
            for flag in self.deoptimization_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.deoptimization_param:
                self.add_to_flags_param(cfg, flag, self.deoptimization_param)
                
        if(self.interpreter):
            for flag in self.interpreter_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.interpreter_param:
                self.add_to_flags_param(cfg, flag,self.interpreter_param)
                
        if(self.memory):
            for flag in self.memory_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.memory_param:
                self.add_to_flags_param(cfg, flag,self.memory_param )
                
        if(self.priorities):
            for flag in self.priorities_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.priorities_param:
                self.add_to_flags_param(cfg, flag,self.priorities_param )
                
        if(self.temporary):
            for flag in self.temporary_bool:
                self.add_to_flags_bool(cfg, flag)
            for flag in self.temporary_param:
                self.add_to_flags_param(cfg, flag,self.temporary_param )
        
        
        run_time=self.execute_program()
        temp_improvement=float((self.default_metric-run_time)/self.default_metric)
        if temp_improvement>= self.improvement:
            self.improvement=temp_improvement
            self.append_to_config_file(self.flags)
            self.append_to_config_file("Improvement: %s" %self.improvement)
            self.append_to_config_file("Configuration Found At: %s" %datetime.datetime.now())
            
        return Result(time=run_time)
    
    @abc.abstractmethod
    def execute_program(self):
        """
        should contain code to run the program
        and extract the runtime from the output
            
        return runtime
        """
        return 0
    
    def get_default_time(self):
        """
        anything need to done before running the program (example : java source to bytecode compilation)
        should go here
        
        generally run execute_program with empty flags
        to get default runtime
        """
        self.flags = ''
        default_time = self.execute_program()
        print 'Default Configuration Metric:',str(default_time)
        self.append_to_config_file('Default Configuration Metric:'+str(default_time))
        return float(default_time)
    
