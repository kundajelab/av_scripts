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

PWM_SAMPLING_MODE = util.enum(bestHit="bestHit", default="default");

def getFileNamePieceFromOptions(options):
    return "pwm-"+options.pwmName+"_pwmSampMode-"+options.pwmSamplingMode+"_pcProb"+str(options.pseudocountProb); 

def getParentArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", required=True); 
    parser.add_argument("--pseudocountProb", type=float, default=0.0); 
    parser.add_argument("--pwmSamplingMode", default=PWM_SAMPLING_MODE.default, choices=PWM_SAMPLING_MODE.vals);
    return parser;

def getSpecfiedPwmFromPwmFile(options):
    import pwm;
    pwms = pwm.readPwm(fp.getFileHandle(options.motifsFile), pseudocountProb=options.pseudocountProb);
    if options.pwmName not in pwms:
        raise RuntimeError("pwmName "+options.pwmName+" not in "+options.motifsFile); 
    pwm = pwms[options.pwmName];    
    return pwm;

def processOptions(options):
    pwm = getSpecfiedPwmFromPwmFile(options);    
    options.pwm = pwm;
    if (options.pwmSamplingMode==PWM_SAMPLING_MODE.bestHit):
        print("Best pwm hit for "+options.pwmName+" is "+options.pwm.bestHit); 

def getPwmSample(options):
    if (options.pwmSamplingMode == PWM_SAMPLING_MODE.default):
        return options.pwm.sampleFromPwm();
    elif (options.pwmSamplingMode == PWM_SAMPLING_MODE.bestHit):
        return options.pwm.bestHit;
    else:
        raise RuntimeError("Unsupported pwm sampling mode: "+str(options.pwmSamplingMode));
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[getPwmParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args();
    processOptions(options);

    outputFileName = "pwmSamples_"+getFileNamePieceFromOptions(options)+"_numSamples-"+str(options.numSamples)+".txt";
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        outputFileHandle.write("synthPos"+str(i)+"\t"+getPwmSample(options)+"\n");
    outputFileHandle.close();
    
