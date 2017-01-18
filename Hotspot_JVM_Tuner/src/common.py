'''
#Author:SapientS
#Date:24/10/2014
#This file contains some simple functionalities which needed to perform the JVM tuner. 
#SapientS
'''
 
import re

'''These methods to get the min max values for a given default value '''
def get_max(default):
    max = default
    if default>=0:
        if default==0:
            max=0 #10
        else:
            max= default + (default/2)
    else:
        max = default - (default/2)
    return max



def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b



def get_min(default):
    min = default
    if default>=0:
        min= default - (default/2)
    else:
        min = default + (default/2)
    return min
'''Exception handled conversion to convert string to a int or float.'''
def convert_to_numeric(string):
    value = 0
    
    if isfloat(string):
        #print 'Float Detected...'
        return float(string)
    elif isint(string):
        #print 'Integer Detected..'
        return long(string)
    else:
        print 'Invalid Default Value.'
        return value