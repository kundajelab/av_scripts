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
import math

def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

def sampleIndex(options, stringToEmbedInLen, thingToEmbedLen):
    """
        to make sure motifs don't overlap, will keep resampling till get a valid location
    """
    if (options.positionalMode == POSITIONAL_MODE.centralBpToEmbedIn):
        #have performed checks to ensure that centralBp is <= seqLength and >= pwmSize
        #the shorter region is going on the left in case stringToEmbedIn is even length and centralBpToEmbedIn is odd
        startIndexForRegionToEmbedIn = int(stringToEmbedInLen/2) - int(options.centralBp/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(options.centralBp, thingToEmbedLen); 
    elif (options.positionalMode == POSITIONAL_MODE.centralBpToEmbedOutside):
        #choose whether to embed in the left or the right
        if random.random() > 0.5:
            left=True;
        else:
            left=False;
        #embeddableLength is the length of the region we are considering embedding in
        embeddableLength = 0.5*(stringToEmbedInLen-options.centralBpToEmbedOutside);
        #if len(stringToEmbedIn)-options.centralBpToEmbedOutside is odd, the longer region
        #goes on the left (inverse of the shorter embeddable region going on the left in
        #the centralBpToEmbedIn case
        if (left):
            embeddableLength = math.ceil(embeddableLength);
            startIndexForRegionToEmbedIn = 0;
        else:
            embeddableLength = math.floor(embeddableLength);
            startIndexForRegionToEmbedIn = math.ceil((stringToEmbedInLen-options.centralBpToEmbedOutside)/2)+options.centralBpToEmbedOutside;
        indexToSample = startIndexForRegionToEmbedIn+sampleIndexWithinRegionOfLength(embeddableLength, thingToEmbedLen)
    else: #uniform positional sampling
        indexToSample = sampleIndexWithinRegionOfLength(stringToEmbedInLen, thingToEmbedLen);
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
    if (options.quantMotif_mode == QUANTITY_OF_MOTIFS_MODE.poisson):
        #sample from poisson
    return sample;

def sampleQuantOfMotifs(options):
    if (options.quantMotif_mode in [QUANTITY_OF_MOTIFS_MODE.poisson]):
        sample = None;
        while(sample == None or (options.quantMotif_min is not None and sample < options.quantMotif_min)):
            #sample from the distribution, resample if condition not met.
            sample = sampleFromDistribution(options);
        return sample; 

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.positionalMode, 'positionalMode')
                ,util.ArgumentToAdd(options.centralBp, 'centBp')]
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
                            ])
     
    #POSITIONAL_MODE.embedInCentralBp
    if (options.positionalMode == POSITIONAL_MODE.embedInCentralBp):
        if (options.centralBp > options.seqLength):
            raise RuntimeError("centralBp must be <= seqLength; "+str(options.centralBpToEmbedIn)+" and "+str(options.seqLength)+" respectively");
        if (options.centralBp < options.pwm.pwmSize):
            raise RuntimeError("if mode is embedInCentralBp, then centralBp must be at least as large as the pwmSize; "+str(options.centralBpToEmbedIn)+" and "+str(options.pwm.pwmSize));
    #POSITIONAL_MODE.embedOutsideCentralBp
    if (options.positionalMode == POSITIONAL_MODE.embedOutsideCentralBp):
        if ((options.seqLength-options.centralBp)/2 < options.pwm.pwmSize):
            raise RuntimeError("(options.seqLength-options.centralBp)/2 should be >= options.pwm.pwmSize; got len ",str(options.seqLength)+", centralBpToEmbedOutside "+str(options.centralBp)+" and pwmSize "+str(options.pwm.pwmSize));

POSITIONAL_MODE = {uniform='uniform', embedInCentralBp='embedInCentralBp', embedOutsideCentralBp='embedOutsideCentralBp', gaussian='gaussian'};
QUANTITY_OF_MOTIFS_MODE = {poisson='poisson'};
positionalModeOptionsAssociatedWithCentralBp = [POSITIONAL_MODE.embedInCentralBp, POSITIONAL_MODE.embedOutsideCentralBp];

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[makePwmSamples.getParentArgparse(),synthetic.getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    parser.add_argument("--quantMotif_mode", choices=QUANTITY_OF_MOTIFS_MODE.vals);
    parser.add_argument("--quantMotif_mean", type=float, help="Parameter associated with quantity of pwm sampling conditions");
    parser.add_argument("--quantMotif_min", type=int, help="Minimum number of pwms in a given sequence");
    parser.add_argument("--positionalMode", choices=POSITIONAL_MODE.vals);
    parser.add_argument("--centralBp", type=int, help="Associated with positional mode options "+["\t".join(str(x) for x in positionalModeOptionsAssociatedWithCentralBp)]);
    options = parser.parse_args();
    makePwmSamples.processOptions(options);
    makePwmSamples.performChecksOnOptions(options);     
    performChecksOnOptions(options);

    outputFileName = ("embedded"
                        +getFileNamePieceFromOptions(options) #this one includes the underscore if there are opts
                        +"_"+synthetic.getFileNamePieceFromOptions(options)
                        +makePwmSamples.getFileNamePieceFromOptions(options)
                        +"_numSamples-"+str(options.numSamples)+".txt"); 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        motifString, logOdds = embedMotif(options)
        outputFileHandle.write("synthPos"+str(i)+"\t"+motifString+"\n");
    outputFileHandle.close();
