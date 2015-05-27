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
import random;

PWM_SAMPLING_MODE = util.enum(bestHit="bestHit", default="default");

def getFileNamePieceFromOptions(options):
    return ("pwm-"+options.pwmName
            +"_pwmSampMode-"+options.pwmSamplingMode
            +"_pcProb"+str(options.pseudocountProb)
            +"_revCmpPrb"+str(options.reverseComplementProb)); 

def getParentArgparse():
    parser = pwm.getLoadPwmArgparse();
    parser.add_argument("--pwmSamplingMode", default=PWM_SAMPLING_MODE.default, choices=PWM_SAMPLING_MODE.vals);
    parser.add_argument("--reverseComplementProb", default=0.5, type=float, help="Optional: probability of reverse complementing");
    return parser;

def performChecksOnOptions(options):
    if (options.reverseComplementProb < 0.0 or options.reverseComplementProb > 1.0):
        raise RuntimeError("Reverse complement prob should be >= 0.0 and <= 1.0; was "+str(options.reverseComplementProb));

def processOptions(options):
    thePwm = pwm.getSpecfiedPwmFromPwmFile(options);    
    options.pwm = thePwm;
    if (options.pwmSamplingMode==PWM_SAMPLING_MODE.bestHit):
        print("Best pwm hit for "+options.pwmName+" is "+options.pwm.bestHit); 

def getPwmSample(options):
    if (options.pwmSamplingMode == PWM_SAMPLING_MODE.default):
        seq, generationProb = options.pwm.sampleFromPwm();
    elif (options.pwmSamplingMode == PWM_SAMPLING_MODE.bestHit):
        seq, generationProb = options.pwm.bestHit, 1.0;
    else:
        raise RuntimeError("Unsupported pwm sampling mode: "+str(options.pwmSamplingMode));
    
    ##apply the reverse complement thing
    if (random.random() < options.reverseComplementProb): 
        seq = util.reverseComplement(seq);
    return seq, generationProb; 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[getPwmParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args();
    performChecksOnOptions(options);
    processOptions(options);

    outputFileName = "pwmSamples_"+getFileNamePieceFromOptions(options)+"_numSamples-"+str(options.numSamples)+".txt";
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\tlogOdds\n");
    for i in xrange(options.numSamples):
        pwm, logOdds = getPwmSample(options)
        outputFileHandle.write("synthPos"+str(i)+"\t"+str(pwm)+"\t"+str(logOdds)+"\n");
    outputFileHandle.close();
    
