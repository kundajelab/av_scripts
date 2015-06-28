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

def printSequences(outputFileName, sequenceSetGenerator):
    ofh = fp.getFileHandle(outputFileName, 'w');
    ofh.write("seqName\tsequence\n");
    generatedSequences = sequenceSetGenerator.generateSequences(); #returns a generator
    for generateSequence in generatedSequences:
        ofh.write(generateSequence.seqName+"\t"+generateSequence.seq+"\n");
    ofh.close(); 
    infoFilePath = fp.getFileNameParts(outputFileName).getFilePathWithTransformation(lambda x: "info_"+x, extension=".txt");
    
    import json;
    ofh = fp.getFileHandle(infoFilePath, 'w');
    ofh.write(json.dumps(sequenceSetGenerator.getJsonableObject(), indent=4, separators=(',', ': '))); 
    ofh.close(); 

class GeneratedSequence(object):
    def __init__(self, seqName, seq, embeddings):
        self.seqName = seqName;
        self.seq = seq;
        self.embeddings = embeddings;

class Embedding(object):
    def __init__(self, seq, startPos):
        self.seq = seq;
        self.startPos = startPos;

class SequenceSetGenerator(object):
    def generateSequences(self):
        """
            returns a generator of GeneratedSequence objects
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class GenerateSequenceNTimes(SequenceSetGenerator):
    def __init__(self, sequenceGenerator, N):
        self.sequenceGenerator = sequenceGenerator;
        self.N = N;
    def generateSequences(self):
        for i in xrange(self.N):
            yield self.sequenceGenerator.generateSequence();
    def getJsonableObject(self):
        return OrderedDict([("numSeq",self.N),("sequenceGenerator",self.sequenceGenerator.getJsonableObject())]);

class SingleSequenceGenerator(object):
    def generateSequence(self):
        """
            returns GeneratedSequence object
        """
        raise NotImplementedError(); 
    def getJsonableObject(self):
        raise NotImplementedError();

class EmbedInABackground(SingleSequenceGenerator):
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
    def getBackgroundGenerator(self):
        return self.backgroundGenerator;
    def getJsonableObject(self):
        return OrderedDict([("class", "EmbedInABackground")
                            ,("namePrefix", self.namePrefix)
                            ,("backgroundGenerator",self.backgroundGenerator.getJsonableObject())
                            ,("embedders",[x.getJsonableObject() for x in self.embedders])
                            ]);

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
    def getJsonableObject(self):
        raise NotImplementedError();

class XOREmbedder(object):
    def __init__(self, embedder1, embedder2, probOfFirst):
        self.embedder1 = embedder1;
        self.embedder2 = embedder2;
        self.probOfFirst = probOfFirst;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        if (random.random() < self.probOfFirst):
            embedder = self.embedder1;
        else:
            embedder = self.embedder2;
        return embedder.embed(backgroundStringArr, priorEmbeddedThings);
    def getJsonableObject(self):
        return OrderedDict([ ("class", "XOREmbedder")
                            ,("embedder1", self.embedder1.getJsonableObject())
                            ,("embedder2", self.embedder2.getJsonableObject())
                            ,("probOfFirst", self.probOfFirst)]);

class RepeatedEmbedder(Embedder):
    def __init__(self, embedder, quantityGenerator):
        self.embedder = embedder;
        self.quantityGenerator = quantityGenerator;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        quantity = self.quantityGenerator.generateQuantity();
        for i in range(quantity):
            self.embedder.embed(backgroundStringArr, priorEmbeddedThings);
    def getJsonableObject(self):
        return OrderedDict([("class", "RepeatedEmbedder"), ("embedder", self.embedder.getJsonableObject()), ("quantityGenerator", self.quantityGenerator.getJsonableObject())]);

class QuantityGenerator(object):
    def generateQuantity(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class FixedQuantityGenerator(QuantityGenerator):
    def __init__(self, quantity):
        self.quantity = quantity;
    def generateQuantity(self):
        return self.quantity;
    def getJsonableObject(self):
        return "fixedQuantity-"+str(self.quantity);

class PoissonQuantityGenerator(QuantityGenerator):
    def __init__(self, mean):
        self.mean = mean;
    def generateQuantity(self):
        return np.random.poisson(self.mean);  
    def getJsonableObject(self):
        return "poisson-"+str(self.mean);

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
    def getJsonableObject(self):
        return OrderedDict([("min",self.theMin), ("max",self.theMax), ("quantityGenerator", self.quantityGenerator.getJsonableObject())]);

class ZeroInflater(QuantityGenerator):
    def __init__(self, quantityGenerator, zeroProb):
        self.quantityGenerator=quantityGenerator;
        self.zeroProb = zeroProb
    def generateQuantity(self):
        if (random.random() < self.zeroProb):
            return 0;
        else:
            return self.quantityGenerator.generateQuantity();
    def getJsonableObject(self):
        return OrderedDict([("class", "ZeroInflater"), ("zeroProb", self.zeroProb), ("quantityGenerator", self.quantityGenerator.getJsonableObject())]); 

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
    def getJsonableObject(self):
        return OrderedDict([("substringGenerator", self.substringGenerator.getJsonableObject()), ("positionGenerator", self.positionGenerator.getJsonableObject())]);

class PositionGenerator(object):
    def generatePos(self, lenBackground, lenSubstring):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class UniformPositionGenerator(PositionGenerator):
    def generatePos(self, lenBackground, lenSubstring):
        return sampleIndexWithinRegionOfLength(lenBackground, lenSubstring); 
    def getJsonableObject(self):
        return "uniform";

class InsideCentralBp(PositionGenerator):
    def __init__(self, centralBp):
        self.centralBp = centralBp;
    def generatePos(self, lenBackground, lenSubstring):
        startIndexForRegionToEmbedIn = int(lenBackground/2) - int(self.centralBp/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(self.centralBp, lenSubstring); 
        return int(indexToSample);
    def getJsonableObject(self):
        return "insideCentral-"+str(self.centralBp);

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
    def getJsonableObject(self):
        return "outsideCentral-"+str(self.centralBp);

def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

class AbstractSubstringGenerator(object):
    def generateSubstring(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class TransformedSubstringGenerator(AbstractSubstringGenerator):
    """
        Takes a substringGenerator and a set of AbstractTransformation objects,
        applies the transformations to the generated substring
    """
    def __init__(self, substringGenerator, transformations):
        self.substringGenerator = substringGenerator;
        self.transformations = transformations;
    def generateSubstring(self):
        baseSubstringArr = [x for x in self.substringGenerator.generateSubstring()];
        for transformation in transformations:
            baseSubstringArr = transformation.transform(baseSubstringArr);
        return "".join(baseSubstringArr);
    def getJsonableObject(self):
        return OrderedDict([("class", "TransformedSubstringGenerator"), ("substringGenerator", self.substringGenerator.getJsonableObject()), ("transformations", [x.getJsonableObject() for x in self.transformations])]); 

class AbstractTransformation(object):
    """
        takes an array of characters, applies some transformation, returns an
        array of characters (may be the same (mutated) one or a different one)
    """
    def transform(self, stringArr):
        """
            stringArr is an array of characters.
            Returns an array of characters.
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class RevertToReference(AbstractTransformation):
    """
        for a series of mutations, reverts the supplied string to the reference
        ("unmutated") string
    """
    def __init__(self, setOfMutations):
        """
            setOfMutations: instance of AbstractSetOfMutations
        """
        self.setOfMutations = setOfMutations;
    def transform(self, stringArr):
        for mutation in self.setOfMutations.getMutationsArr():
            mutation.revert(stringArr);
        return stringArr;
    def getJsonableObject(self):
        return OrderedDict([("class", "RevertToReference"), ("setOfMutations", self.setOfMutations.getJsonableObject())]); 

class AbstractApplySingleMutationFromSet(AbstractTransformation):
    def __init__(self, setOfMutations):
        self.setOfMutations = setOfMutations;
    def transformation(self, stringArr):
        selectedMutation = self.selectMutation();
        selectedMutation.applyMutation(stringArr);
        return stringArr;
    def selectMutation(self):
        raise NotImplementedError();
    def getClassName(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        return OrderedDict([("class", self.getClassName()), ("selectedMutations", self.setOfMutations.getJsonableObject())]);

class ChooseMutationAtRandom(AbstractApplySingleMutationFromSet):
    def selectMutation(self):
        mutationsArr = self.setOfMutations.getMutationsArr();
        return mutationsArr[int(random.random()*len(mutationsArr))];
    def getClassName(self):
        return "ChooseMutationAtRandom";

class AbstractSetOfMutations(object):
    def __init__(self, mutationsArr):
        self.mutationsArr = mutationsArr;
    def getMutationsArr(self):
        return self.mutationsArr;
    def getJsonableObject(self):
        raise NotImplementedError();

class TopNMutationsFromPwmRelativeToBestHit(AbstractSetOfMutations):
    def __init__(self, pwm, N, bestHitMode):
        self.pwm = pwm;
        self.N = N;
        self.bestHitMode = bestHitMode;
        mutationsArr = self.pwm.computeSingleBpMutationEffects(self.bestHitMode);
        super(TopNMutationsFromPwmRelativeToBestHit, self).__init__(mutationsArr); 
    def getJsonableObject(self):
        return OrderedDict([("class","TopNMutationsFromPwmRelativeToBestHit"), ("pwm",self.pwm.name), ('N',self.N), ("bestHitMode", self.bestHitMode)]); 

class TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs(TopNMutationsFromPwmRelativeToBestHit):
    def __init__(self, loadedMotifs, pwmName, N, bestHitMode):
        self.loadedMotifs = loadedMotifs;
        super(TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs, self).__init__(self.loadedMotifs.getPwm(pwmName), N, bestHitMode);
    def getJsonableObject(self):
        obj = super(TopNMutationsFromPwmRelativeToBestHit, self).getJsonableObject();
        obj['loadedMotifs'] = self.loadedMotifs.getJsonableObject();

class ReverseComplementWrapper(AbstractSubstringGenerator):
    """
        Wrapper around a AbstractSubstringGenerator that reverse complements it
        with the specified probability.
    """
    def __init__(self, substringGenerator, reverseComplementProb=0.5):
        self.reverseComplementProb=reverseComplementProb;
        self.substringGenerator=substringGenerator;
    def generateSubstring(self):
        seq = self.substringGenerator.generateSubstring();
        if (random.random() < self.reverseComplementProb): 
            seq = util.reverseComplement(seq);
        return seq;
    def getJsonableObject(self):
        return OrderedDict([("class", "ReverseComplementWrapper"), ("reverseComplementProb",self.reverseComplementProb), ("substringGenerator", self.substringGenerator.getJsonableObject())]);

class PwmSubstringGenerator(AbstractSubstringGenerator):
    def __init__(self, pwm):
        self.pwm = pwm;

class PwmSampler(PwmSubstringGenerator):
    def generateSubstring(self):
        return self.pwm.sampleFromPwm()[0];
    def getJsonableObject(self):
        return "sample-"+self.pwm.name; 

class PwmSubstringGeneratorUsingLoadedMotifs(PwmSubstringGenerator):
    def __init__(self, loadedMotifs, motifName, pwmSubstringGeneratorClass):
        self.loadedMotifs = loadedMotifs;
        self.motifName = motifName;
        self.pwmSubstringGenerator = pwmSubstringGeneratorClass(self.loadedMotifs.getPwm(self.motifName));
    def generateSubstring(self):
        return self.pwmSubstringGenerator.generateSubstring();
    def getJsonableObject(self):
        return OrderedDict([("motifName", self.motifName), ("pwmSubstringGenerator", self.pwmSubstringGenerator.getJsonableObject()), ("loadedMotifs",self.loadedMotifs.getJsonableObject())]);

class PwmSamplerFromLoadedMotifs(PwmSubstringGeneratorUsingLoadedMotifs):
    def __init__(self, loadedMotifs, motifName):
        super(PwmSamplerFromLoadedMotifs, self).__init__(loadedMotifs, motifName, PwmSampler);

class BestHitPwm(PwmSubstringGenerator):
    def generateSubstring(self):
        return self.pwm.bestHit; 
    def getJsonableObject(self):
        return "bestHit-"+self.pwm.name;

class BestHitPwmFromLoadedMotifs(PwmSubstringGeneratorUsingLoadedMotifs):
    def __init__(self, loadedMotifs, motifName):
        super(BestHitPwmFromLoadedMotifs, self).__init__(loadedMotifs, motifName, BestHitPwm);

class AbstractLoadedMotifs(object):
    """
        A class that contains instances of pwm.PWM loaded from a file.
        The pwms can be accessed by name.
    """
    def __init__(self, fileName, pseudocountProb=0.0, background=util.DEFAULT_BACKGROUND_FREQ):
        """
            fileName: the path to the file to laod
            pseudocountProb: if some of the pwms have 0 probability for
            some of the positions, will add the specified pseudocountProb
            to the rows of the pwm and renormalise.
        """
        self.fileName = fileName;
        fileHandle = fp.getFileHandle(fileName);
        self.pseudocountProb = pseudocountProb;
        self.background = background;
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
    def getJsonableObject(self):
        return OrderedDict([("fileName", self.fileName), ("pseudocountProb",self.pseudocountProb), ("background", self.background)]);

class LoadedEncodeMotifs(AbstractLoadedMotifs):
    def getReadPwmAction(self, recordedPwms):
        currentPwm = util.VariableWrapper(None);
        def action(inp, lineNumber):
            if (inp.startswith(">")):
                inp = inp.lstrip(">");
                inpArr = inp.split();
                motifName = inpArr[0];
                currentPwm.var = pwm.PWM(motifName, background=self.background);
                recordedPwms[currentPwm.var.name] = currentPwm.var;
            else:
                #assume that it's a line of the pwm
                assert currentPwm.var is not None;
                inpArr = inp.split();
                summaryLetter = inpArr[0];
                currentPwm.var.addRow([float(x) for x in inpArr[1:]]);
        return action;

class BackgroundGenerator(object):
    def generateBackground(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class ZeroOrderBackgroundGenerator(BackgroundGenerator):
    def __init__(self, seqLength):
        self.seqLength = seqLength;
    def generateBackground(self):
        return generateString_zeroOrderMarkov(length=self.seqLength);
    def getJsonableObject(self):
        return "zeroOrderBackground-"+str(self.seqLength);

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

     

