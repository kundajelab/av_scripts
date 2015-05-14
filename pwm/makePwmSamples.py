#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import argparse;
import pwm;
import fileProcessing as fp;

def getFileNamePieceFromOptions(options):
    return "pwm-"+options.pwmName; 

def getParentArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", required=True); 
    return parser;

def getSpecfiedPwmFromPwmFile(options):
    import pwm;
    pwms = pwm.readPwm(fp.getFileHandle(options.motifsFile));
    if options.pwmName not in pwms:
        raise RuntimeError("pwmName "+options.pwmName+" not in "+options.motifsFile); 
    pwm = pwms[options.pwmName];    
    return pwm;
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[getPwmParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args();

    pwm = getSpecfiedPwmFromPwmFile(options);    

    outputFileName = "pwmSamples_"+getFileNamePieceFromOptions(options)+"_numSamples-"+str(options.numSamples)+".txt";
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        outputFileHandle.write("synthPos"+str(i)+"\t"+pwm.sampleFromPwm()+"\n");
    outputFileHandle.close();
    
