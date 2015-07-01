#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import argparse;
from synthetic import synthetic;
import pwm;
from pwm import makePwmSamples;
import random;
import math
import numpy as np;

def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

def sampleIndex(options, stringToEmbedInLen, thingToEmbedLen):
    """
        to make sure motifs don't overlap, will keep resampling till get a valid location
    """
    if (options.positionalMode == POSITIONAL_MODE.embedInCentralBp):
        #have performed checks to ensure that centralBp is <= seqLength and >= pwmSize
        #the shorter region is going on the left in case stringToEmbedIn is even length and centralBpToEmbedIn is odd
        startIndexForRegionToEmbedIn = int(stringToEmbedInLen/2) - int(options.centralBp/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(options.centralBp, thingToEmbedLen); 
    elif (options.positionalMode == POSITIONAL_MODE.embedOutsideCentralBp):
        #choose whether to embed in the left or the right
        if random.random() > 0.5:
            left=True;
        else:
            left=False;
        #embeddableLength is the length of the region we are considering embedding in
        embeddableLength = 0.5*(stringToEmbedInLen-options.centralBp);
        #if len(stringToEmbedIn)-options.centralBp is odd, the longer region
        #goes on the left (inverse of the shorter embeddable region going on the left in
        #the centralBpToEmbedIn case
        if (left):
            embeddableLength = math.ceil(embeddableLength);
            startIndexForRegionToEmbedIn = 0;
        else:
            embeddableLength = math.floor(embeddableLength);
            startIndexForRegionToEmbedIn = math.ceil((stringToEmbedInLen-options.centralBp)/2)+options.centralBp;
        indexToSample = startIndexForRegionToEmbedIn+sampleIndexWithinRegionOfLength(embeddableLength, thingToEmbedLen)
    elif (options.positionalMode == POSITIONAL_MODE.uniform): #uniform positional sampling
        indexToSample = sampleIndexWithinRegionOfLength(stringToEmbedInLen, thingToEmbedLen);
    else:
        raise RuntimeError("Unsupported positional mode: "+options.positionalMode);
    assert int(indexToSample)==indexToSample;
    indexToSample=int(indexToSample);
    return indexToSample;

def embedInAvailableLocation(options, stringToEmbedInArr, thingToEmbedArr, priorEmbeddedThings):
    indexToSample = None;
    embeddingAttempts=0;
    while ((indexToSample==None) or (indexToSample in priorEmbeddedThings)):
        embeddingAttempts += 1;
        if (embeddingAttempts%10 == 0):
            #we are resampling until we get a success
            print("Warning: "+str(embeddingAttempts)+" embedding attempts");
            if (embeddingAttempts > 1000):
                raise RuntimeError("It's too hard to do non overlapping embeddings; perhaps put a cap on the amount of stuff you're trying to cram into a given seq? Right now "+str(len(priorEmbeddedThings.keys()))+" positions are off limits");
        indexToSample = sampleIndex(options, len(stringToEmbedInArr), len(thingToEmbedArr));
    stringToEmbedInArr[indexToSample:indexToSample+len(thingToEmbedArr)] = thingToEmbedArr;
    for i in xrange(indexToSample-len(thingToEmbedArr)+1, indexToSample+len(thingToEmbedArr)-1):
        priorEmbeddedThings[i] = thingToEmbedArr;

def embedMotif(options):
    stringToEmbedIn = synthetic.generateString(options);
    stringToEmbedInArr = [x for x in stringToEmbedIn];
    numMotifs = sampleQuantOfMotifs(options);
    priorEmbeddedThings = {};
    for i in range(numMotifs): 
        pwmSample,logProb = makePwmSamples.getPwmSample(options);
        embedInAvailableLocation(options, stringToEmbedInArr, [x for x in pwmSample], priorEmbeddedThings); 
    return "".join(stringToEmbedInArr);

def sampleFromDistribution(options):
    if (options.quantMotifMode == QUANTITY_OF_MOTIFS_MODE.poisson):
        return np.random.poisson(options.quantMotifMean);
    else:
        raise RuntimeError("Unsupported quantMotifMode "+options.quantMotifMode);

def sampleQuantOfMotifs(options):
    if (options.quantMotifMode in [QUANTITY_OF_MOTIFS_MODE.poisson]):
        sample = None;
        samplingAttempts = 0;
        while(sample == None or (options.quantMotifMin is not None and sample < options.quantMotifMin) or (options.quantMotifMax is not None and sample > options.quantMotifMax)):
            samplingAttempts += 1;
            if (samplingAttempts%10 == 0):
                print("Warning: have made "+str(samplingAttempts)+" quantMotif sampling attempts");
            #sample from the distribution, resample if condition not met.
            sample = sampleFromDistribution(options);
        return sample;
    elif (options.quantMotifMode in [QUANTITY_OF_MOTIFS_MODE.fixed]):
        if int(options.quantMotifMean)!=options.quantMotifMean:
            raise RuntimeError("quantMotifMean should be integer if quantMotifsMode is "+options.quantMotifMode);
        return int(options.quantMotifMean);
    else:
        raise RuntimeError("Unsupported quantMotifMode "+options.quantMotifMode); 

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.positionalMode, 'posMode')
                ,util.ArgumentToAdd(options.centralBp, 'centBp')
                ,util.ArgumentToAdd(options.quantMotifMode, 'qtMtfMd')
                ,util.ArgumentToAdd(options.quantMotifMean, 'qtMtfMu')
                ,util.ArgumentToAdd(options.quantMotifMin, 'qtMtfMin')
                ,util.ArgumentToAdd(options.quantMotifMax, 'qtMtfMax')]
    toReturn = util.addArguments("", argsToAdd);
    return toReturn;

def performChecksOnOptions(options):
    import conditionCheck;

    #centralBp should be specified if and only if positional mode is among...
    conditionCheck.AllOrNone([  conditionCheck.ValueIsSetInOptions(options, 'centralBp')
                                ,conditionCheck.ValueAmongOptions(
                                    options.positionalMode
                                    , 'positionalMode'
                                    , [POSITIONAL_MODE.embedInCentralBp, POSITIONAL_MODE.embedOutsideCentralBp]
                                )
                            ], description="centralBp should be specified iff position mode is among certain options:").enforce();
    #quantMotifMean should be specified iff certain quantity sampling modes are chosen
    conditionCheck.AllOrNone([ conditionCheck.ValueIsSetInOptions(options, 'quantMotifMean')
                                ,conditionCheck.ValueAmongOptions(
                                    options.quantMotifMode
                                    , 'quantMotifMode'
                                    , [QUANTITY_OF_MOTIFS_MODE.poisson, QUANTITY_OF_MOTIFS_MODE.fixed]
                                )
                            ], description="quantMotifMean should be specified iff certain quantity sampling modes are chosen").enforce();
    minAndMaxQuantMotifModes = [QUANTITY_OF_MOTIFS_MODE.poisson];
    #quantMotifMin should only be specified if certain quantMotif modes are chosen
    conditionCheck.Any([conditionCheck.ValueAmongOptions(options.quantMotifMode, 'quantMotifMode', minAndMaxQuantMotifModes)
                        ,conditionCheck.Notter(conditionCheck.ValueIsSetInOptions(options, 'quantMotifMin'))]
                        ,description="quantMotifMin should only be specified if certain quantMotif modes are chosen").enforce();
    #quantMotifMax should only be specified if certain quantMotif modes are chosen
    conditionCheck.Any([conditionCheck.ValueAmongOptions(options.quantMotifMode, 'quantMotifMode', minAndMaxQuantMotifModes)
                        ,conditionCheck.Notter(conditionCheck.ValueIsSetInOptions(options, 'quantMotifMax'))]
                        ,description="quantMotifMax should only be specified if certain quantMotif modes are chosen").enforce();
     
    #POSITIONAL_MODE.embedInCentralBp
    if (options.positionalMode == POSITIONAL_MODE.embedInCentralBp):
        if (options.centralBp > options.seqLength):
            raise RuntimeError("centralBp must be <= seqLength; "+str(options.centralBp)+" and "+str(options.seqLength)+" respectively");
        if (options.centralBp < options.pwm.pwmSize):
            raise RuntimeError("if mode is embedInCentralBp, then centralBp must be at least as large as the pwmSize; "+str(options.centralBp)+" and "+str(options.pwm.pwmSize));
    #POSITIONAL_MODE.embedOutsideCentralBp
    if (options.positionalMode == POSITIONAL_MODE.embedOutsideCentralBp):
        if ((options.seqLength-options.centralBp)/2 < options.pwm.pwmSize):
            raise RuntimeError("(options.seqLength-options.centralBp)/2 should be >= options.pwm.pwmSize; got len ",str(options.seqLength)+", centralBp "+str(options.centralBp)+" and pwmSize "+str(options.pwm.pwmSize));

POSITIONAL_MODE = util.enum(uniform='unif', embedInCentralBp='embedInCent', embedOutsideCentralBp='embedOutCent', gaussian='gauss');
QUANTITY_OF_MOTIFS_MODE = util.enum(poisson='poisson', fixed='fixed');
positionalModeOptionsAssociatedWithCentralBp = [POSITIONAL_MODE.embedInCentralBp, POSITIONAL_MODE.embedOutsideCentralBp];

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[makePwmSamples.getParentArgparse(),synthetic.getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    parser.add_argument("--quantMotifMode", choices=QUANTITY_OF_MOTIFS_MODE.vals, required=True);
    parser.add_argument("--quantMotifMean", type=float, help="Parameter associated with quantity of pwm sampling conditions");
    parser.add_argument("--quantMotifMin", type=int, help="Minimum number of pwms in a given sequence");
    parser.add_argument("--quantMotifMax", type=int, help="Max number of pwms in a given sequence");
    parser.add_argument("--positionalMode", choices=POSITIONAL_MODE.vals, default=POSITIONAL_MODE.uniform);
    parser.add_argument("--centralBp", type=int, help="Associated with some positional mode options.");
    options = parser.parse_args();
    makePwmSamples.processOptions(options);
    makePwmSamples.performChecksOnOptions(options);     
    performChecksOnOptions(options);

    outputFileName = ("embedded"
                        +getFileNamePieceFromOptions(options) #this one includes the underscore if there are opts
                        +"_"+synthetic.getFileNamePieceFromOptions(options)
                        +makePwmSamples.getFileNamePieceFromOptions(options)
                        +"_numSamp-"+str(options.numSamples)+".txt"); 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        embeddedString = embedMotif(options)
        outputFileHandle.write("synth"+str(i)+"\t"+embeddedString+"\n");
    outputFileHandle.close();
