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
from kmerCountPackage import seqToKmerIds;

def fastaToKmerIndices(options):
    fastaIterator = fp.FastaIterator(fp.getFileHandle(options.fastaInput),progressUpdate=options.progressUpdate);
    outputFilePrefix = util.addArguments("kmerIds", [util.ArgumentToAdd(options.kmerLength, "k")]);
    outputFileName = fp.getFileNameParts(options.fastaInput).getFilePathWithTransformation(lambda x: outputFilePrefix+"_"+x, extension=".txt.gz");
    outputFileHandle = fp.getFileHandle(outputFileName, 'w'); 
    numSeqs=0;
    batchOfSeqNamesAndSequencesVariableWrapper = util.VariableWrapper([]);
    for (key, sequence) in fastaIterator:
        numSeqs+=1;
        batchOfSeqNamesAndSequencesVariableWrapper.var.append((key,sequence));
        if (numSeqs%options.batchSize==0):
            seqToKmerIds.processBatchOfSeqNamesAndSequences(
                batchOfSeqNamesAndSequencesVariableWrapper.var
                ,outputFileHandle
                ,options);
            batchOfSeqNamesAndSequencesVariableWrapper.var=[]; 
    seqToKmerIds.processBatchOfSeqNamesAndSequences(batchOfSeqNamesAndSequencesVariableWrapper.var, outputFileHandle, options); 

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--fastaInput", required=True);    
    parser.add_argument("--kmerLength", type=int, required=True);
    parser.add_argument("--batchSize", type=int, default=100);
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();

    fastaToKmerIndices(options)
