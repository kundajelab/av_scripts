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

def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

def embedMotif(options):
    stringToEmbedIn = synthetic.generateString(options);
    pwmSample,logProb = makePwmSamples.getPwmSample(options);
    if (options.centralBpToEmbedIn is None):
        indexToSample = sampleIndexWithinRegionOfLength(len(stringToEmbedIn), len(pwmSample));
    else:
        startIndexForRegionToEmbedIn = int(len(stringToEmbedIn)/2) - int(options.centralBpToEmbedIn/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(options.centralBpToEmbedIn, len(pwmSample)); 
    return (stringToEmbedIn[0:indexToSample]
            +pwmSample
            +stringToEmbedIn[indexToSample+len(pwmSample):]), logProb;

def getFileNamePieceFromOptions(options):
    toReturn = (("centBp-"+str(options.centralBpToEmbedIn) if options.centralBpToEmbedIn is not None else "")) 
    if len(toReturn) > 0:
        toReturn = "_"+toReturn;
    return toReturn;

def performChecksOnOptions(options):
    #options.centralBpToEmbedIn
    if (options.centralBpToEmbedIn is not None):
        if (options.centralBpToEmbedIn > options.seqLength):
            raise RuntimeError("centralBpToEmbedIn must be <= seqLength; "+str(options.centralBpToEmbedIn)+" and "+str(options.seqLength)+" respectively");
        if (options.centralBpToEmbedIn < options.pwm.pwmSize):
            raise RuntimeError("centralBpToEmbedIn must be at least as large as the pwmSize; "+str(options.centralBpToEmbedIn)+" and "+str(options.pwm.pwmSize));

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[makePwmSamples.getParentArgparse(),synthetic.getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    parser.add_argument("--centralBpToEmbedIn", type=int, help="Central n bp to embed into");
    options = parser.parse_args();
    makePwmSamples.processOptions(options);
    makePwmSamples.performChecksOnOptions(options);     
    performChecksOnOptions(options);

    outputFileName = ("embedded"
                        +getFileNamePieceFromOptions(options) #this one includes the underscore if there are opts
                        +"_"+synthetic.getFileNamePieceFromOptions(options)
                        +"_"+makePwmSamples.getFileNamePieceFromOptions(options)
                        +"_numSamples-"+str(options.numSamples)+".txt"); 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        motifString, logOdds = embedMotif(options)
        outputFileHandle.write("synthPos"+str(i)+"\t"+motifString+"\n");
    outputFileHandle.close();
