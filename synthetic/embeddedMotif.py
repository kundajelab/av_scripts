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

def embedMotif(options):
    stringToEmbedIn = synthetic.generateString(options);
    pwmSample,logProb = makePwmSamples.getPwmSample(options); 
    assert len(pwmSample) <= len(stringToEmbedIn);
    indexToSample = int(random.random()*((len(stringToEmbedIn)-len(pwmSample)) + 1));
    return (stringToEmbedIn[0:indexToSample]
            +pwmSample
            +stringToEmbedIn[indexToSample+len(pwmSample):]), logProb;

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[makePwmSamples.getParentArgparse(),synthetic.getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args();
    makePwmSamples.processOptions(options); 
    outputFileName = ("embedded_"+synthetic.getFileNamePieceFromOptions(options)
                        +"_"+makePwmSamples.getFileNamePieceFromOptions(options)
                        +"_numSamples-"+str(options.numSamples)+".txt"); 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\tlogOdds\n");
    for i in xrange(options.numSamples):
        motifString, logProb = embedMotif(options)
        outputFileHandle.write("synthPos"+str(i)+"\t"+motifString+"\n");
    outputFileHandle.close();
