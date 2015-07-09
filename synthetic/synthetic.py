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
    """
        outputFileName: string
        sequenceSetGenerator: instance of AbstractSequenceSetGenerator
        Given an output filename, and an instance of AbstractSequenceSetGenerator,
        will call the sequence set generator and print the generated sequences
        to the output file. Will also create a file "info_outputFileName.txt"
        in the samedirectory as outputFileName that contains all the information
        about sequenceSetGenerator.
    """
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

class AbstractPositionGenerator(object):
    """
        Given the length of the background sequence and the length
        of the substring you are trying to embed, will return a start position
        to embed the substring at.
    """
    def generatePos(self, lenBackground, lenSubstring):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class UniformPositionGenerator(AbstractPositionGenerator):
    """
        samples a start position to embed the substring in uniformly at random;
        does not return positions that are too close to the end of the
        background sequence to embed the full substring.
    """
    def generatePos(self, lenBackground, lenSubstring):
        return sampleIndexWithinRegionOfLength(lenBackground, lenSubstring); 
    def getJsonableObject(self):
        return "uniform";
uniformPositionGenerator = UniformPositionGenerator();

class InsideCentralBp(AbstractPositionGenerator):
    """
        returns a position within the central region of a background
        sequence, sampled uniformly at random
    """
    def __init__(self, centralBp):
        """
            centralBp: the number of bp, centered in the middle of the background,
            from which to sample the position. Is NOT +/- centralBp around the
            middle (is +/- centralBp/2 around the middle).
            If the background sequence is even and centralBp is odd, the shorter
            region will go on the left.
        """
        self.centralBp = centralBp;
    def generatePos(self, lenBackground, lenSubstring):
        if (lenBackground < self.centralBpToEmbedIn):
            raise RuntimeError("The background length should be atleast as long as self.centralBpToEmbedIn; is "+str(lenBackground)+" and "+str(self.centralBpToEmbedIn)+" respectively");
        startIndexForRegionToEmbedIn = int(lenBackground/2) - int(self.centralBp/2);
        indexToSample = startIndexForRegionToEmbedIn + sampleIndexWithinRegionOfLength(self.centralBp, lenSubstring); 
        return int(indexToSample);
    def getJsonableObject(self):
        return "insideCentral-"+str(self.centralBp);

class OutsideCentralBp(AbstractPositionGenerator):
    """
        Returns a position OUTSIDE the central region of a background sequence,
        sampled uniformly at random. Complement of InsideCentralBp.
    """
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


class GeneratedSequence(object):
    """
        An object representing a sequence that has been
        generated.
    """
    def __init__(self, seqName, seq, embeddings):
        """
            seqName: string
            seq: generated sequence (string)
            embeddings: array of Embedding objects
        """
        self.seqName = seqName;
        self.seq = seq;
        self.embeddings = embeddings;

class Embedding(object):
    """
        Represents something that has been embedded in
        a sequence
    """
    def __init__(self, what, startPos):
        """
            what: object representing the thing that has been embedded. Should have __str__ and __len__ defined
            startPos: that position relative to the start of the
            parent sequence at which seq has been embedded
        """
        self.what = what;
        self.startPos = startPos;

class AbstractSequenceSetGenerator(object):
    """
        class that is used to return a generator for a collection
        of generated sequences.
    """
    def generateSequences(self):
        """
            returns a generator of GeneratedSequence objects
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        """
            returns an object representing the details of this, which
            can be converted to json.
        """
        raise NotImplementedError();

class GenerateSequenceNTimes(AbstractSequenceSetGenerator):
    """
        If you just want to use a generator of a single sequence and
        call it N times, use this class.
    """
    def __init__(self, singleSequenceGenerator, N):
        """
            singleSequenceGenerator: an instance of AbstractSingleSequenceGenerator
        """
        self.singleSequenceGenerator = singleSequenceGenerator;
        self.N = N;
    def generateSequences(self):
        """
            calls singleSequenceGenerator N times.
        """
        for i in xrange(self.N):
            yield self.singleSequenceGenerator.generateSequence();
    def getJsonableObject(self):
        return OrderedDict([("numSeq",self.N),("singleSequenceGenerator",self.singleSequenceGenerator.getJsonableObject())]);

class AbstractSingleSequenceGenerator(object):
    """
        When called, generates a single sequence
    """
    def __init__(self, namePrefix=None):
        """
            namePrefix: the GeneratedSequence object has a field for the object's name; this is
            the prefix associated with that name. The suffix is the value of a counter that
            is incremented every time 
        """
        self.namePrefix = namePrefix if namePrefix is not None else "synth";
        self.sequenceCounter = 0;
    def generateSequence(self):
        """
            returns GeneratedSequence object
        """
        raise NotImplementedError(); 
    def getJsonableObject(self):
        """
            returns an object representing the details of this, which
            can be converted to json.
        """
        raise NotImplementedError();

class EmbedInABackground(AbstractSingleSequenceGenerator):
    """
        Takes a backgroundGenerator and a series of embedders. Will
        generate the background and then call each of the embedders in
        succession. Then returns the result.
    """
    def __init__(self, backgroundGenerator, embedders, namePrefix=None):
        """
            backgroundGenerator: instance of AbstractBackgroundGenerator
            embedders: array of instances of AbstractEmbedder
            namePrefix: see parent
        """
        super(EmbedInABackground, self).__init__(namePrefix);
        self.backgroundGenerator = backgroundGenerator;
        self.embedders = embedders;
    def generateSequence(self):
        """
            generates a background using self.backgroundGenerator, splits it into an array,
            and passes it to each of self.embedders in turn for embedding things.
            returns an instance of GeneratedSequence
        """
        backgroundString = self.backgroundGenerator.generateBackground();
        backgroundStringArr = [x for x in backgroundString];
        #priorEmbeddedThings keeps track of what has already been embedded
        priorEmbeddedThings = PriorEmbeddedThings_numpyArrayBacked(len(backgroundStringArr));
        for embedder in self.embedders:
            embedder.embed(backgroundStringArr, priorEmbeddedThings);  
        self.sequenceCounter += 1;
        return GeneratedSequence(self.namePrefix+str(self.sequenceCounter), "".join(backgroundStringArr), priorEmbeddedThings.getEmbeddings());
    def getJsonableObject(self):
        """
            see parent
        """
        return OrderedDict([("class", "EmbedInABackground")
                            ,("namePrefix", self.namePrefix)
                            ,("backgroundGenerator",self.backgroundGenerator.getJsonableObject())
                            ,("embedders",[x.getJsonableObject() for x in self.embedders])
                            ]);

class AbstractPriorEmbeddedThings(object):
    """
        class that is used to keep track of what has already been embedded in a sequence
    """
    def canEmbed(self, startPos, endPos):
        """
            returns a boolean indicating whether the region from startPos to endPos is available for embedding
        """
        raise NotImplementedError();
    def addEmbedding(self, startPos, what):
        """
            embeds "what" from startPos to startPos+len(what). Creates an Embedding object
        """
        raise NotImplementedError();
    def getNumOccupiedPos(self):
        """
            returns the number of posiitons that are filled with some kind of embedding
        """
        raise NotImplementedError();
    def getTotalPos(self):
        """
            returns the total number of positions available to embed things in
        """
        raise NotImplementedError();
    def getEmbeddings(self):
        """
            returns a collection of Embedding objects
        """
        raise NotImplementedError();

class PriorEmbeddedThings_numpyArrayBacked(AbstractPriorEmbeddedThings):
    """
        uses a numpy array where positions are set to 1 if they are occupied,
        to determin which positions are occupied and which are not.
        See parent for more documentation.
    """
    def __init__(self, seqLen):
        """
            seqLen: integer indicating length of the sequence you are embedding in
        """
        self.seqLen = seqLen;
        self.arr = np.zeros(seqLen);
        self.embeddings = [];
    def canEmbed(self, startPos, endPos):
        return np.sum(self.arr[startPos:endPos])==0;
    def addEmbedding(self, startPos, what):
        """
            what: instance of Embeddable
        """
        self.arr[startPos:startPos+len(what)] = 1;
        self.embeddings.append(Embedding(what=what, startPos=startPos));
    def getNumOccupiedPos(self):
        return np.sum(self.arr);
    def getTotalPos(self):
        return len(self.arr);
    def getEmbeddings(self):
        return self.embeddings;

class AbstractEmbedder(object):
    """
        class that is used to embed things in a sequence
    """
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        """ 
            backgroundStringArr: array of characters representing the background string
            priorEmbeddedThings: instance of AbstractPriorEmbeddedThings.
            modifies: backgroundStringArr to include whatever this class has embedded
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class AbstractEmbeddable(object):
    """
        Represents a thing which can be embedded. Note that
        an Embeddable + a position = an embedding.
    """
    def __len__(self):
        raise NotImplementedError();
    def __str__(self):
        raise NotImplementedError();
    def canEmbed(self, priorEmbeddedThings, startPos):
        """
            priorEmbeddedThings: instance of AbstractPriorEmbeddedThings
            startPos: the position you are considering embedding self at
            returns a boolean indicating whether self can be embedded at startPos, 
                given the things that have already been embedded.
        """
        raise NotImplementedError();
    def embedInBackgroundStringArr(self, priorEmbeddedThings, backgroundStringArr, startPos):
        """
            Will embed self at startPos in backgroundStringArr, and will update priorEmbeddedThings.
            priorEmbeddedThings: instance of AbstractPriorEmbeddedThings
            backgroundStringArr: an array of characters representing the background
            startPos: the position to embed self at
        """
        raise NotImplementedError(); 

class StringEmbeddable(AbstractEmbeddable):
    """
        represents a string (such as a sampling from a pwm) that is to
        be embedded in a background. See docs for superclass.
    """
    def __init__(self, string):
        self.string = string;
    def __len__(self):
        return len(self.string);
    def __str__(self):
        return self.string;
    def canEmbed(self, priorEmbeddedThings, startPos):
        return priorEmbeddedThings.canEmbed(startPos, startPos+len(self.string))
    def embedInBackgroundStringArr(self, priorEmbeddedThings, backgroundStringArr, startPos):
        backgroundStringArr[startPos:startPos+len(self.string)]=self.string;
        priorEmbeddedThings.addEmbedding(startPos, self.string);

class PairEmbeddable(AbstractEmbeddable):
    """
        Represents a pair of strings that are embedded with some separation.
        Used for motif grammars. See superclass docs.
    """
    def __init__(self, string1, string2, separation, nothingInBetween=True):
        """
            separation: int of positions separating
                string1 and string2
            nothingInBetween: if true, then nothing else is allowed to be
                embedded in the gap between string1 and string2.
        """
        self.string1 = string1;
        self.string2 = string2;
        self.separation = separation;
        self.nothingInBetween = nothingInBetween;
    def __len__(self):
        return len(self.string1)+self.separation+len(self.string2);
    def __str__(self):
        return self.string1+"-Gap"+str(self.separation)+"-"+self.string2;
    def canEmbed(self, priorEmbeddedThings, startPos):
        if (self.nothingInBetween):
            return priorEmbeddedThings.canEmbed(startPos, startPos+len(self));
        else:
            return (priorEmbeddedThings.canEmbed(startPos,startPos+len(self.string1))
                    and priorEmbeddedThings.canEmbed(startPos+len(self.string1)+self.separation, startPos+len(self)));
    def embedInBackgroundStringArr(self, priorEmbeddedThings, backgroundStringArr, startPos):
        backgroundStringArr[startPos:startPos+len(self.string1)] = self.string1;
        backgroundStringArr[startPos+len(self.string1)+self.separation:startPos+len(self)] = self.string2;
        if (self.nothingInBetween):
            priorEmbeddedThings.addEmbedding(startPos, self);
        else:
            priorEmbeddedThings.addEmbedding(startPos, self.string1);
            priorEmbeddedThings.addEmbedding(startPos+len(self.string1)+self.separation, self.string2);

class EmbeddableEmbedder(AbstractEmbedder):
    """
        Embeds instances of AbstractEmbeddable within the background sequence,
        at a position sampled from a distribution. Only embeds at unoccupied
        positions
    """
    def __init__(self, embeddableGenerator, positionGenerator=uniformPositionGenerator):
        """
            embeddableGenerator: instance of AbstractEmbeddableGenerator
            positionGenerator: instance of AbstractPositionGenerator
        """
        self.embeddableGenerator = embeddableGenerator;
        self.positionGenerator = positionGenerator;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        """
            calls self.embeddableGenerator to determine the embeddable to embed. Then
            calls self.positionGenerator to determine the start position at which
            to embed it. If the position is occupied, will resample from
            self.positionGenerator. Will warn if tries to resample too many times.
        """
        embeddable = self.embeddableGenerator.generateEmbeddable();
        canEmbed = False;
        tries = 0;
        while canEmbed==False:
            tries += 1;
            startPos = self.positionGenerator.generatePos(len(backgroundStringArr), len(embeddable));
            canEmbed = embeddable.canEmbed(priorEmbeddedThings, startPos);
            if (tries%10 == 0):
                print("Warning: made "+str(tries)+" at trying to embed "+str(embeddable)+" in region of length "+str(priorEmbeddedThings.getTotalPos())+" with "+str(priorEmbeddedThings.getNumOccupiedPos())+" occupied sites");
        embeddable.embedInBackgroundStringArr(priorEmbeddedThings, backgroundStringArr, startPos);
    def getJsonableObject(self):
        return OrderedDict([("embeddableGenerator", self.embeddableGenerator.getJsonableObject())
                            , ("positionGenerator", self.positionGenerator.getJsonableObject())]);

class XOREmbedder(AbstractEmbedder):
    """
        calls exactly one of the supplied embedders
    """
    def __init__(self, embedder1, embedder2, probOfFirst):
        """
            embedder1 & embedder2: instances of AbstractEmbedder
            probOfFirst: probability of calling the first embedder
        """
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

class RepeatedEmbedder(AbstractEmbedder):
    """
        Wrapper around an embedder to call it multiple times according to sampling
        from a distribution.
    """
    def __init__(self, embedder, quantityGenerator):
        """
            embedder: instance of AbstractEmbedder
            quantityGenerator: instance of AbstractQuantityGenerator
        """
        self.embedder = embedder;
        self.quantityGenerator = quantityGenerator;
    def embed(self, backgroundStringArr, priorEmbeddedThings):
        """
            first calls self.quantityGenerator.generateQuantity(), then calls
            self.embedder a number of times equal to the value returned.
        """
        quantity = self.quantityGenerator.generateQuantity();
        for i in range(quantity):
            self.embedder.embed(backgroundStringArr, priorEmbeddedThings);
    def getJsonableObject(self):
        return OrderedDict([("class", "RepeatedEmbedder"), ("embedder", self.embedder.getJsonableObject()), ("quantityGenerator", self.quantityGenerator.getJsonableObject())]);

class AbstractQuantityGenerator(object):
    """
        class to sample according to a distribution
    """
    def generateQuantity(self):
        """
            returns the sampled value
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class UniformIntegerGenerator(AbstractQuantityGenerator):
    """
        Randomly samples an integer from minVal to maxVal, inclusive.
    """
    def __init__(self, minVal, maxVal):
        self.minVal = minVal;
        self.maxVal = maxVal;
    def generateQuantity(self):
        return self.minVal + int(random.random()*(1+self.maxVal-self.minVal)); #the 1+ makes the max val inclusive
    def getJsonableObject(self):
        return OrderedDict([("class","UniformIntegerGenerator"), ("minVal",self.minVal), ("maxVal",self.maxVal)]);

class FixedQuantityGenerator(AbstractQuantityGenerator):
    """
        returns a fixed number every time generateQuantity is called
    """
    def __init__(self, quantity):
        """
            quantity: the value to return when generateQuantity is called.
        """
        self.quantity = quantity;
    def generateQuantity(self):
        return self.quantity;
    def getJsonableObject(self):
        return "fixedQuantity-"+str(self.quantity);

class PoissonQuantityGenerator(AbstractQuantityGenerator):
    """
        Generates values according to a poisson distribution
    """
    def __init__(self, mean):
        """
            mean: the mean of the poisson distribution
        """
        self.mean = mean;
    def generateQuantity(self):
        return np.random.poisson(self.mean);  
    def getJsonableObject(self):
        return "poisson-"+str(self.mean);

class MinMaxWrapper(AbstractQuantityGenerator):
    """
        Wrapper that restricts a distribution to only return values between the min and
        the max. If a value outside the range is returned, resamples until
        it obtains a value within the range. Warns if it resamples too many times.
    """
    def __init__(self, quantityGenerator, theMin=None, theMax=None):
        """
            quantityGenerator: samples from the distribution to truncate
            theMin: can be None; if so will be ignored
            theMax: can be None; if so will be ignored.
        """
        self.quantityGenerator=quantityGenerator;
        self.theMin=theMin;
        self.theMax=theMax;
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

class ZeroInflater(AbstractQuantityGenerator):
    """
        Wrapper that inflates the number of zeros returned. Flips a coin; if positive,
        will return zero - otherwise will sample from the wrapped distribution (which may still return 0)
    """
    def __init__(self, quantityGenerator, zeroProb):
        """
            quantityGenerator: the distribution to sample from with probability 1-zeroProb
            zeroProb: the probability of just returning 0 without sampling from quantityGenerator
        """
        self.quantityGenerator=quantityGenerator;
        self.zeroProb = zeroProb
    def generateQuantity(self):
        if (random.random() < self.zeroProb):
            return 0;
        else:
            return self.quantityGenerator.generateQuantity();
    def getJsonableObject(self):
        return OrderedDict([("class", "ZeroInflater"), ("zeroProb", self.zeroProb), ("quantityGenerator", self.quantityGenerator.getJsonableObject())]); 

class SubstringEmbedder(EmbeddableEmbedder):
    """
        embeds a single generated substring within the background sequence,
        at a position sampled from a distribution. Only embeds at unoccupied
        positions
    """
    def __init__(self, substringGenerator, positionGenerator=uniformPositionGenerator):
        """
            substringGenerator: instance of AbstractSubstringGenerator
            positionGenerator: instance of AbstractPositionGenerator
        """
        super(SubstringEmbedder, self).__init__(
            SubstringEmbeddableGenerator(substringGenerator)
            , positionGenerator);


def sampleIndexWithinRegionOfLength(length, lengthOfThingToEmbed):
    """
        uniformly at random samples integers from 0 to length-lengthOfThingToEmbedIn
    """
    assert lengthOfThingToEmbed <= length;
    indexToSample = int(random.random()*((length-lengthOfThingToEmbed) + 1));
    return indexToSample;

class AbstractEmbeddableGenerator(object):
    """
        Generates an embeddable, usually for embedding in a background sequence.
    """
    def generateEmbeddable(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class PairEmbeddableGenerator(AbstractEmbeddableGenerator):
    def __init__(self, substringGenerator1, substringGenerator2, separationGenerator):
        """
            substringGenerator1: instance of AbstractSubstringGenerator
            substringGenerator2: instance of AbstractSubstringGenerator
            separationGenerator: instance of AbstractQuantityGenerator
        """
        self.substringGenerator1=substringGenerator1;
        self.substringGenerator2=substringGenerator2;
        self.separationGenerator=separationGenerator;
    def generateEmbeddable(self):
        return PairEmbeddable(
                    self.substringGenerator1.generateSubstring()
                    ,self.substringGenerator2.generateSubstring()
                    ,self.separationGenerator.generateQuantity()
                );
    def getJsonableObject(self):
        return OrderedDict([("class", "PairEmbeddableGenerator")
                            ,("substringGenerator1",self.substringGenerator1.getJsonableObject())
                            ,("substringGenerator2",self.substringGenerator2.getJsonableObject())
                            ,("separationGenerator",self.separationGenerator.getJsonableObject())
                            ]);

class SubstringEmbeddableGenerator(AbstractEmbeddableGenerator):
    def __init__(self, substringGenerator):
        """
            substringGenerator: instance of AbstractSubstringGenerator
        """ 
        self.substringGenerator = substringGenerator;
    def generateEmbeddable(self):
        return StringEmbeddable(self.substringGenerator.generateSubstring());
    def getJsonableObject(self):
        return OrderedDict([("class", "SubstringEmbeddableGenerator"), ("substringGenerator", self.substringGenerator.getJsonableObject())]);

class AbstractSubstringGenerator(object):
    """
        Generates a substring, usually for embedding in a background sequence.
    """
    def generateSubstring(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class FixedSubstringGenerator(object):
    """
        When generateSubstring() is called, always returns the same string.
    """
    def __init__(self, fixedSubstring):
        self.fixedSubstring = fixedSubstring;
    def generateSubstring(self):
        return self.fixedSubstring;
    def getJsonableObject(self):
        return "fixedSubstring-"+self.fixedSubstring; 

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
        #print("orig","".join(baseSubstringArr));
        for transformation in self.transformations:
            baseSubstringArr = transformation.transform(baseSubstringArr);
            #print("tran","".join(baseSubstringArr));
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
            Returns an array of characters that has the transformation applied.
            May mutate stringArr
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
    def transform(self, stringArr): #see parent docs
        for mutation in self.setOfMutations.getMutationsArr():
            mutation.revert(stringArr);
        return stringArr;
    def getJsonableObject(self):
        return OrderedDict([("class", "RevertToReference"), ("setOfMutations", self.setOfMutations.getJsonableObject())]); 

class AbstractApplySingleMutationFromSet(AbstractTransformation):
    """
        Class for applying a single mutation from a set of mutations; used
        to transform substrings generated by another method
    """
    def __init__(self, setOfMutations):
        """
            setOfMutations: instance of AbstractSetOfMutations
        """
        self.setOfMutations = setOfMutations;
    def transform(self, stringArr): #see parent docs
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
    """
        Selects a mutation at random from self.setOfMutations to apply; see parent docs.
    """
    def selectMutation(self):
        mutationsArr = self.setOfMutations.getMutationsArr();
        return mutationsArr[int(random.random()*len(mutationsArr))];
    def getClassName(self):
        return "ChooseMutationAtRandom";

class AbstractSetOfMutations(object):
    """
        Represents a collection of pwm.Mutation objects
    """
    def __init__(self, mutationsArr):
        """
            mutationsArr: array of pwm.Mutation objects
        """
        self.mutationsArr = mutationsArr;
    def getMutationsArr(self):
        return self.mutationsArr;
    def getJsonableObject(self):
        raise NotImplementedError();

class TopNMutationsFromPwmRelativeToBestHit(AbstractSetOfMutations):
    """
        See docs for parent; here, the collection of mutations are the
        top N strongest mutations for a PWM as compared to the best
        match for that pwm.
    """
    def __init__(self, pwm, N, bestHitMode):
        """
            pwm: instance of pwm.PWM
            N: the N in the top N strongest mutations
            bestHitMode: one of pwm.BEST_HIT_MODE; pwm.BEST_HIT_MODE.pwmProb defines the
                topN mutations relative to the probability matrix of the pwm, while
                pwm.BEST_HIT_MODE.logOdds defines the topN mutations relative to the log
                odds matrix computed using the background frequency specified in the
                pwm object.
        """
        self.pwm = pwm;
        self.N = N;
        self.bestHitMode = bestHitMode;
        mutationsArr = self.pwm.computeSingleBpMutationEffects(self.bestHitMode);
        super(TopNMutationsFromPwmRelativeToBestHit, self).__init__(mutationsArr); 
    def getJsonableObject(self):
        return OrderedDict([("class","TopNMutationsFromPwmRelativeToBestHit"), ("pwm",self.pwm.name), ('N',self.N), ("bestHitMode", self.bestHitMode)]); 

class TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs(TopNMutationsFromPwmRelativeToBestHit):
    """
        Like parent, except extracts the pwm.PWM object from an AbstractLoadedMotifs object,
        saving you a few lines of code.
    """
    def __init__(self, loadedMotifs, pwmName, N, bestHitMode):
        self.loadedMotifs = loadedMotifs;
        super(TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs, self).__init__(self.loadedMotifs.getPwm(pwmName), N, bestHitMode);
    def getJsonableObject(self):
        obj = super(TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs, self).getJsonableObject();
        obj['loadedMotifs'] = self.loadedMotifs.getJsonableObject();
        return obj;

class ReverseComplementWrapper(AbstractSubstringGenerator):
    """
        Wrapper around a AbstractSubstringGenerator that reverse complements it
        with the specified probability.
    """
    def __init__(self, substringGenerator, reverseComplementProb=0.5):
        """
            substringGenerator: instance of AbstractSubstringGenerator
            reverseComplementProb: probability of reverse complementing it.
        """
        self.reverseComplementProb=reverseComplementProb;
        self.substringGenerator=substringGenerator;
    def generateSubstring(self):
        seq = self.substringGenerator.generateSubstring();
        if (random.random() < self.reverseComplementProb): 
            seq = util.reverseComplement(seq);
        return seq;
    def getJsonableObject(self):
        return OrderedDict([("class", "ReverseComplementWrapper"), ("reverseComplementProb",self.reverseComplementProb), ("substringGenerator", self.substringGenerator.getJsonableObject())]);

class PwmSampler(AbstractSubstringGenerator):
    """
        samples from the pwm by calling self.pwm.sampleFromPwm
    """
    def __init__(self, pwm):
        self.pwm = pwm;
    def generateSubstring(self):
        return self.pwm.sampleFromPwm()[0];
    def getJsonableObject(self):
        return OrderedDict([("class", "PwmSampler"), ("motifName",self.pwm.name)]); 

class PwmSamplerFromLoadedMotifs(PwmSampler):
    """
        convenience wrapper class for instantiating parent by pulling the pwm given the name
        from an AbstractLoadedMotifs object (it basically extracts the pwm for you)
    """
    def __init__(self, loadedMotifs, motifName):
        self.loadedMotifs = loadedMotifs;
        super(PwmSamplerFromLoadedMotifs, self).__init__(loadedMotifs.getPwm(motifName));
    def getJsonableObject(self):
        obj = super(PwmSamplerFromLoadedMotifs, self).getJsonableObject();
        obj['loadedMotifs'] = self.loadedMotifs.getJsonableObject();
        return obj;

class BestHitPwm(AbstractSubstringGenerator):
    """
        always returns the best possible match to the pwm in question when called
    """
    def __init__(self, pwm, bestHitMode):
        self.pwm = pwm;
        self.bestHitMode = bestHitMode;
    def generateSubstring(self):
        return self.pwm.getBestHit(self.bestHitMode); 
    def getJsonableObject(self):
        return OrderedDict([("class", "BestHitPwm"), ("pwm",self.pwm.name), ("bestHitMode", self.bestHitMode)]);

class BestHitPwmFromLoadedMotifs(BestHitPwm):
    """
        convenience wrapper class for instantiating parent by pulling the pwm given the name
        from an AbstractLoadedMotifs object (it basically extracts the pwm for you)
    """
    def __init__(self, loadedMotifs, motifName, bestHitMode):
        self.loadedMotifs = loadedMotifs;
        super(BestHitPwmFromLoadedMotifs, self).__init__(loadedMotifs.getPwm(motifName), bestHitMode);
    def getJsonableObject(self):
        obj = super(BestHitPwmFromLoadedMotifs, self).getJsonableObject();
        obj['loadedMotifs'] = self.loadedMotifs.getJsonableObject();
        return obj;

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
        """
            returns the pwm.PWM instance with the specified name.
        """
        return self.recordedPwms[name];
    def getReadPwmAction(self, recordedPwms):
        """
            This is the action that is to be performed on each line of the
            file when it is read in. recordedPwms is an OrderedDict that
            stores instances of pwm.PWM
        """
        raise NotImplementedError();
    def getJsonableObject(self):
        return OrderedDict([("fileName", self.fileName), ("pseudocountProb",self.pseudocountProb), ("background", self.background)]);

class LoadedEncodeMotifs(AbstractLoadedMotifs):
    """
        This class is specifically for reading files in the encode motif
        format - specifically the motifs.txt file that contains Pouya's motifs
    """
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

class AbstractBackgroundGenerator(object):
    """
        Returns the sequence that the embeddings are subsequently inserted into.
    """
    def generateBackground(self):
        raise NotImplementedError();
    def getJsonableObject(self):
        raise NotImplementedError();

class ZeroOrderBackgroundGenerator(AbstractBackgroundGenerator):
    """
        returns a sequence with 40% GC content. Each base is sampled independently.
    """
    def __init__(self, seqLength, discreteDistribution=util.DEFAULT_BASE_DISCRETE_DISTRIBUTION):
        """
            seqLength: the length of the sequence to return
            discereteDistribution: instance of util.DiscreteDistribution
        """
        self.seqLength = seqLength;
        self.discreteDistribution = discreteDistribution;
    def generateBackground(self):
        return generateString_zeroOrderMarkov(length=self.seqLength, discreteDistribution=self.discreteDistribution);
    def getJsonableObject(self):
        return OrderedDict([("class","zeroOrderMarkovBackground"), ("length", self.seqLength), ("distribution", self.discreteDistribution.valToFreq)]);

class RepeatedSubstringBackgroundGenerator(AbstractBackgroundGenerator):
    def __init__(self, substringGenerator, repetitions):
        """
            substringGenerator: instance of AbstractSubstringGenerator
            repetitions: the number of times to call substringGenerator
            returns the concatenation of all the calls to the substringGenerator
        """
        self.substringGenerator = substringGenerator;
        self.repetitions = repetitions;
    def generateBackground(self):
        toReturn = [];
        for i in xrange(self.repetitions):
            toReturn.append(self.substringGenerator.generateSubstring());
        return "".join(toReturn);
    def getJsonableObject(self):
        return OrderedDict([("class", "RepeatedSubstringBackgroundGenerator"), ("substringGenerator", self.substringGenerator.getJsonableObject()), ("repetitions", self.repetitions)]);
        

###
#Older API below...this was just set up to generate the background sequence
###

def getGenerationOption(string): #for yaml serialisation
    return util.getFromEnum(GENERATION_OPTION, "GENERATION_OPTION", string);
GENERATION_OPTION = util.enum(zeroOrderMarkov="zrOrdMrkv");

def getFileNamePieceFromOptions(options):
    return options.generationOption+"_seqLen"+str(options.seqLength); 

def generateString_zeroOrderMarkov(length, discreteDistribution=util.DEFAULT_BASE_DISCRETE_DISTRIBUTION):
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
