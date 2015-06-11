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
from pwm import makePwmSamples;
from pwm import pwm;
import numpy as np;
import random;
import fileProcessing as fp;
import math;
from collections import OrderedDict;

class GeneratedSequence(object):
    def __init__(self, seqName, seq, embeddings):
        self.seqName = seqName;
        self.seq = seq;
        self.embeddings = embeddings;

class Embedding(object):
    def __init__(self, seq, startPos):
        self.seq = seq;
        self.startPos = startPos;

class SequenceSimulator(object):
    def generateSequence(self):
        """
            returns a GeneratedSequence object
        """
        raise NotImplementedError(); 

class EmbedInABackground(SequenceSimulator):
    def __init__(self, backgroundGenerator, embedders, namePrefix="synth"):
        """
            backgroundGenerator: instance of BackgroundGenerator
            embedders: accept the string array and the occupied positions, and embed in them
        """
        self.backgroundGenerator = backgroundGenerator;
        self.embedders = embedders;
        self.sequenceCounter = 0;
        self.namePrefix = namePrefix;
    def generateSequence(self):
        backgroundString = self.backgroundGenerator.generateBackground();
        backgroundStringArr = [x for x in backgroundString];
        priorEmbeddedThings = PriorEmbeddedThings_numpyArrayBacked(len(backgroundStringArr));
        for embedder in self.embedders:
            embedder.embed(backgroundStringArr, priorEmbeddedThings);  
        self.sequenceCounter += 1;
        return GeneratedSequence(self.namePrefix+str(self.sequenceCounter), "".join(backgroundStringArr), priorEmbeddedThings.getEmbeddings());

class PriorEmbeddedThings(object):
    def canEmbed(self, startPos, endPos):
        raise NotImplementedError();
    def addEmbedding(self, startPos, what):
        raise NotImplementedError();
    def getNumOccupiedPos(self):
        raise NotImplementedError();
    def getTotalPos(self):
        raise NotImplementedError();
    def getEmbeddings(self):
        raise NotImplementedError();

class PriorEmbeddedThings_numpyArrayBacked(object):
    def __init__(self, seqLen):
        self.seqLen = seqLen;
        self.arr = np.zeros(seqLen);
        self.embeddings = [];
    def canEmbed(self, startPos, endPos):
        return np.sum(self.arr[startPos:endPos])==0;
    def addEmbedding(self, startPos, what):
        self.arr[startPos:startPos+len(what)] = 1;
        self.embeddings.append(Embedding(seq=what, startPos=startPos));
    def getNumOccupiedPos(self):
        return np.sum(self.arr);
    def getTotalPos(self):
        return len(self.arr);
    def getEmbeddings(self):
        return self.embeddings;

class Embedder(object):
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        raise NotImplementedError();

class RepeatedEmbedder(Embedder):
    def __init__(self, embedder, quantityGenerator):
        self.embedder = embedder;
        self.quantityGenerator = quantityGenerator;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        quantity = self.quantityGenerator.generateQuantity();
        for i in range(quantity):
            self.embedder.embed(backgroundStringArr, priorEmbeddedThings);

class QuantityGenerator(object):
    def generateQuantity(self):
        raise NotImplementedError();

class FixedQuantityGenerator(QuantityGenerator):
    def __init__(self, quantity):
        self.quantity = quantity;
    def generateQuantity(self):
        return self.quantity;

class PoissonQuantityGenerator(QuantityGenerator):
    def __init__(self, mean):
        self.mean = mean;
    def generateQuantity(self):
        return np.random.poisson(self.mean);  

class MinMaxWrapper(QuantityGenerator):
    def __init__(self, quantityGenerator, theMin=None, theMax=None):
        self.quantityGenerator=quantityGenerator;
        self.theMin=theMin;
        self.theMax=theMax;
        assert self.theMin is not None or self.theMax is not None;
        assert self.quantityGenerator is not None;
    def generateQuantity(self):
        tries=0;
        while (True):
            tries += 1;
            quantity = self.quantityGenerator.generateQuantity();
            if ((self.theMin is None or quantity >= self.theMin) and (self.theMax is None or quantity <= self.theMax)):
                return quantity;
            if (tries%10 == 0):
                print("warning: made "+str(tries)+" at trying to sample from distribution with min/max limits");

class SubstringEmbedder(Embedder):
    def __init__(self, substringGenerator, positionGenerator):
        self.substringGenerator = substringGenerator;
        self.positionGenerator = positionGenerator;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        substring = self.substringGenerator.generateSubstring();
        canEmbed = False;
        tries = 0;
        while canEmbed==False:
            tries += 1;
            startPos = self.positionGenerator.generatePos(len(backgroundStringArr), len(substring));
            canEmbed = priorEmbeddedThings.canEmbed(startPos, startPos+len(substring));
            if (tries%10 == 0):
                print("Warning: made "+str(tries)+" at trying to embed substring of length "+str(len(substring))+" in region of length "+str(priorEmbeddedThings.getTotalPos())+" with "+str(priorEmbeddedThings.getNumOccupiedPos())+" occupied sites");
        backgroundStringArr[startPos:startPos+len(substring)]=substring;
        priorEmbeddedThings.addEmbedding(startPos, substring);

class PositionGenerator(object):
    def generatePos(self, lenBackground, lenSubstring):
        raise NotImplementedError();

class UniformPositionGenerator(PositionGenerator):
    def generatePos(self, lenBackground, lenSubstring):
        return sampleIndexWithinRegionOfLength(lenBackground, lenSubstring); 

class InsideCentralBp(PositionGenerator):
    def __init__(self, centralBp):
        self.centralBp = centralBp;
    def generatePos(self, lenBackground, lenSubstring):
        startIndexForRegionToEmbedIn = int(lenBackground/2) - int(self.centralBp/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(self.centralBp, lenSubstring); 
        return int(indexToSample);

class OutsideCentralBp(PositionGenerator):
    def __init__(self, centralBp):
        self.centralBp = centralBp;
    def generatePos(self, lenBackground, lenSubstring):
        #choose whether to embed in the left or the right
        if random.random() > 0.5:
            left=True;
        else:
            left=False;
        #embeddableLength is the length of the region we are considering embedding in
        embeddableLength = 0.5*(lenBackground-self.centralBp);
        #if lenBackground-self.centralBp is odd, the longer region
        #goes on the left (inverse of the shorter embeddable region going on the left in
        #the centralBpToEmbedIn case
        if (left):
            embeddableLength = math.ceil(embeddableLength);
            startIndexForRegionToEmbedIn = 0;
        else:
            embeddableLength = math.floor(embeddableLength);
            startIndexForRegionToEmbedIn = math.ceil((lenBackground-self.centralBp)/2)+self.centralBp;
        indexToSample = startIndexForRegionToEmbedIn+sampleIndexWithinRegionOfLength(embeddableLength, lenSubstring)
        return int(indexToSample);

def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

class SubstringGenerator(object):
    def generateSubstring(self):
        raise NotImplementedError();

class ReverseComplementWrapper(SubstringGenerator):
    def __init__(self, substringGenerator, reverseComplementProb=0.5):
        self.reverseComplementProb=reverseComplementProb;
        self.substringGenerator=substringGenerator;
    def generateSubstring(self):
        seq = self.substringGenerator.generateSubstring();
        if (random.random() < self.reverseComplementProb): 
            seq = util.reverseComplement(seq);
        return seq;

class PwmSampler(SubstringGenerator):
    def __init__(self, pwm):
        self.pwm = pwm;
    def generateSubstring(self):
        return self.pwm.sampleFromPwm()[0];

class PwmSamplerFromLoadedMotifs(PwmSampler):
    def __init__(self, loadedMotifs, motifName):
        super(PwmSamplerFromLoadedMotifs, self).__init__(loadedMotifs.getPwm(motifName));

class LoadedMotifs(object):
    def __init__(self, fileName, pseudocountProb=0.0):
        fileHandle = fp.getFileHandle(fileName);
        self.pseudocountProb = pseudocountProb;
        self.recordedPwms = OrderedDict();
        action = self.getReadPwmAction(self.recordedPwms);
        fp.performActionOnEachLineOfFile(
            fileHandle = fileHandle
            ,transformation=fp.trimNewline
            ,action=action
        );
        for pwm in self.recordedPwms.values():
            pwm.finalise(pseudocountProb=self.pseudocountProb);
    def getPwm(self, name):
        return self.recordedPwms[name];
    def getReadPwmAction(self, recordedPwms):
        raise NotImplementedError();

class LoadedEncodeMotifs(LoadedMotifs):
    def getReadPwmAction(self, recordedPwms):
        currentPwm = util.VariableWrapper(None);
        def action(inp, lineNumber):
            if (inp.startswith(">")):
                inp = inp.lstrip(">");
                inpArr = inp.split();
                motifName = inpArr[0];
                currentPwm.var = pwm.PWM(motifName);
                recordedPwms[currentPwm.var.name] = currentPwm.var;
            else:
                #assume that it's a line of the pwm
                assert currentPwm.var is not None;
                inpArr = inp.split();
                summaryLetter = inpArr[0];
                currentPwm.var.addRow([float(x) for x in inpArr[1:]]);
        return action;
         

class BestHitPwm(SubstringGenerator):
    def __init__(self, pwm):
        self.pwm = pwm;
    def generateSubstring(self):
        return self.bestHit; 

class BackgroundGenerator(object):
    def generateBackground(self):
        raise NotImplementedError();

class ZeroOrderBackgroundGenerator(BackgroundGenerator):
    def __init__(self, seqLength):
        self.seqLength = seqLength;
    def generateBackground(self):
        return generateString_zeroOrderMarkov(length=self.seqLength);

###
#Older API below...this was just set up to generate the background sequence
###

def getGenerationOption(string): #for yaml serialisation
    return util.getFromEnum(GENERATION_OPTION, "GENERATION_OPTION", string);
GENERATION_OPTION = util.enum(zeroOrderMarkov="zrOrdMrkv");

def getFileNamePieceFromOptions(options):
    return options.generationOption+"_seqLen"+str(options.seqLength); 

def generateString_zeroOrderMarkov(length, discreteDistribution=util.DEFAULT_DISCRETE_DISTRIBUTION):
    """
        discreteDistribution: instance of util.DiscreteDistribution
    """
    sampledArr = util.sampleNinstancesFromDiscreteDistribution(length, discreteDistribution);
    return "".join(sampledArr);

def generateString(options):
    if options.generationOption==GENERATION_OPTION.zeroOrderMarkov:
        return generateString_zeroOrderMarkov(length=options.seqLength);
    else:
        raise RuntimeError("Unsupported generation option: "+str(options.generationOption));

def getParentArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--generationOption", default=GENERATION_OPTION.zeroOrderMarkov, choices=GENERATION_OPTION.vals);
    parser.add_argument("--seqLength", type=int, required=True, help="Length of the sequence to generate");
    return parser; 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[getParentArgparse()]);
    parser.add_argument("--numSamples", type=int, required=True);
    options = parser.parse_args(); 

    outputFileName = getFileNamePieceFromOptions(options)+"_numSamples-"+str(options.numSamples)+".txt";
 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.numSamples):
        outputFileHandle.write("synthNeg"+str(i)+"\t"+generateString(options)+"\n");
    outputFileHandle.close();

     

