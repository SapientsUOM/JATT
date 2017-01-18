'''
#Author:Milinda Fernando
#Date:18/05/2015
# This program contains the functionality to collect the standard benchmark results with tuned and default configurations. 
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

argparser = argparse.ArgumentParser()
argparser.add_argument('--default',help='source file to compile (only give name e.g: MatrixMultiply)')
argparser.add_argument('--Tuned',help='source file to compile (only give name e.g: MatrixMultiply)')
argparser.add_argument('--Iterations',help='source file to compile (only give name e.g: MatrixMultiply)')
argparser.add_argument('--Output',help='source file to compile (only give name e.g: MatrixMultiply)')

