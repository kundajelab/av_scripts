#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import profileSequences;
import numpy as np;

CHAR_TO_NUMBER_MAPPING={'A': 0, 'a': 0, 'C': 1, 'c': 1, 'G': 2, 'g': 2, 'T':3, 't':3, 'N':4, 'n':4}
ALPHABET_SIZE=5;

def getKmerOrdering(kmerLength):
    totalNumKmers = ALPHABET_SIZE**kmerLength;
    arrToReturn = [None]*totalNumKmers; #array of kmers in order of their ids
    placeValueArray = [ALPHABET_SIZE**i for i in range(kmerLength)][::-1]
    allKmers = profileSequences.getAllCharacterCombos(kmerLength, ['A','C','G','T','N']);    
    for kmer in allKmers:
        kmerIdx = np.sum(np.array([CHAR_TO_NUMBER_MAPPING[x] for x in kmer])*placeValueArray);
        arrToReturn[kmerIdx]=kmer;
    assert all([x is not None for x in arrToReturn]);
    return arrToReturn;
 
def processBatchOfSeqNamesAndSequences(batch, outputFileHandle, options):
    batchOfSeqNames = [x[0] for x in batch];
    batchOfSequences = [x[1] for x in batch];
    batchOfKmerIds = seqsToKmerIds(batchOfSequences, options.kmerLength);
    for seqName, kmerIds in zip(batchOfSeqNames, batchOfKmerIds):
        outputFileHandle.write(seqName+"\t");
        outputFileHandle.write(" ".join(str(int(x)) for x in kmerIds))
        outputFileHandle.write("\n");

def seqsToKmerIds(batchOfSeqs,kmerLength):
    #map characters to numbers
    batchOfCharIds = np.array([[CHAR_TO_NUMBER_MAPPING[x] for x in seq] for seq in batchOfSeqs]); 
    #toReturn will contain the kmer ids of the kmers in the seqs
    batchOfKmerIdsToReturn = np.empty((len(batchOfSeqs), len(batchOfSeqs[0])-kmerLength+1));
    #[::-1] is for reversal. First position has highest place val.
    #[None,None,:] is for: [batchIdx, kmerIdx, posWithinKmer]
    placeValueArray = np.array([ALPHABET_SIZE**i for i in range(kmerLength)][::-1])[None,None,:]; 
    for offset in range(kmerLength):
        numKmersThatFit = int((len(batchOfSeqs[0])-offset)/kmerLength)
        lastKmerForOffsetEnd = numKmersThatFit*kmerLength + offset;
        batchOfKmerIdsForOffset = np.sum(np.reshape(batchOfCharIds[:,offset:lastKmerForOffsetEnd], (-1,numKmersThatFit,kmerLength))*placeValueArray,axis=2);
        batchOfKmerIdsToReturn[:,slice(offset,lastKmerForOffsetEnd,kmerLength)] = batchOfKmerIdsForOffset;
    return batchOfKmerIdsToReturn;
