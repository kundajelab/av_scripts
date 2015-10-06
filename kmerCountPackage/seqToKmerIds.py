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
import numpy as np;

CHAR_TO_NUMBER_MAPPING={'A': 0, 'a': 0, 'C': 1, 'c': 1, 'G': 2, 'g': 2, 'T':3, 't':3, 'N':4, 'n':4}

def seqsToKmerIds(batchOfSeqs,k):
    #map characters to numbers
    batchOfCharIds = np.array([[CHAR_TO_NUMBER_MAPPING[x] for x in seq] for seq in batchOfSeqs]); 
    #toReturn will contain the kmer ids of the kmers in the seqs
    batchOfKmerIdsToReturn = np.empty((len(batchOfSeqs), len(batchOfSeqs[0])-k+1));
    #[::-1] is for reversal. First position has highest place val.
    #[None,None,:] is for: [batchIdx, kmerIdx, posWithinKmer]
    placeValueArray = np.array([5**i for i in range(k)][::-1])[None,None,:]; 
    for offset in range(k):
        numKmersThatFit = int((len(batchOfSeqs[0])-offset)/k)
        lastKmerForOffsetEnd = numKmersThatFit*k + offset;
        batchOfKmerIdsForOffset = np.sum(np.reshape(batchOfCharIds[:,offset:lastKmerForOffsetEnd], (-1,numKmersThatFit,k))*placeValueArray,axis=2);
        batchOfKmerIdsToReturn[:,slice(offset,lastKmerForOffsetEnd,k)] = batchOfKmerIdsForOffset;
    return batchOfKmerIdsToReturn;
