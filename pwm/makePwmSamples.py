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
from pwm import pwm;
import fileProcessing as fp;

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", required=True); 
    parser.add_argument("--N", type=int, required=True);
    options = parser.parse_args();

    pwms = pwm.readPwm(fp.getFileHandle(options.motifsFile));
    if options.pwmName not in pwms:
        raise RuntimeError("pwmName "+options.pwmName+" not in "+options.motifsFile); 
    pwm = pwms[options.pwmName];    

    outputFileName = "pwmSamples_"+options.pwmName+"_numSeq_"+str(options.N)+".txt";
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.N):
        outputFileHandle.write("sampling_"+options.pwmName+str(i)+"\t"+pwm.sampleFromPwm()+"\n");
    outputFileHandle.close();
    
