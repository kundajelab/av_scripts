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
import synthetic;
import pwm;
from pwm import makePwmSamples;
import random;

def embedMotif(stringToEmbedIn, pwmToSampleFrom):
    assert pwmToSampleFrom.pwmSize <= len(stringToEmbedIn);
    indexToSample = int(random.random()*(len(stringToEmbedIn)-(pwmToSampleFrom.pwmSize + 1)));
    return (stringToEmbedIn[0:indexToSample]
            +pwmToSampleFrom.sampleFromPwm()
            +stringToEmbedIn[indexToSample+pwmToSampleFrom.pwmSize:]);

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[makePwmSamples.getParentArgparse(),synthetic.getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args();

    pwmToSampleFrom = makePwmSamples.getSpecfiedPwmFromPwmFile(options);
    outputFileName = ("embedded_"+synthetic.getFileNamePieceFromOptions(options)
                        +"_"+makePwmSamples.getFileNamePieceFromOptions(options)
                        +"_numSamples-"+str(options.numSamples)+".txt"); 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        stringToEmbedIn = synthetic.generateString(options); 
        outputFileHandle.write("synthPos"+str(i)+"\t"+embedMotif(stringToEmbedIn, pwmToSampleFrom)+"\n");
    outputFileHandle.close();
