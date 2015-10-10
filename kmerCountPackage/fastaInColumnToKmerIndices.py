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

def fastaInColumnToKmerIndices(options):
    outputFilePrefix = util.addArguments("kmerIds", [util.ArgumentToAdd(options.kmerLength, "k")]);
    outputFileName = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: outputFilePrefix+"_"+x, extension=".txt.gz");
    outputFileHandle = fp.getFileHandle(outputFileName, 'w'); 
    
    batchOfSeqNamesAndSequencesVariableWrapper = util.VariableWrapper([]);
    def actionAtEndOfBatch():
        seqToKmerIds.processBatchOfSeqNamesAndSequences(batchOfSeqNamesAndSequencesVariableWrapper.var, outputFileHandle, options); 
        batchOfSeqNamesAndSequencesVariableWrapper.var=[];
    
    def actionOnLineInBatch(inp, lineNumber):
        key = inp[options.idColumn] if options.idColumn is not None else "seq"+str(lineNumber);        
        sequence = inp[options.columnWithSequence]; 
        batchOfSeqNamesAndSequencesVariableWrapper.var.append((key,sequence));
    
    fp.performActionInBatchesOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.inputFile)
        ,batchSize=options.batchSize
        ,actionOnLineInBatch=actionOnLineInBatch
        ,actionAtEndOfBatch=actionAtEndOfBatch
        ,progressUpdate=options.progressUpdate
        ,ignoreInputTitle=options.titlePresent
        ,transformation=fp.defaultTabSeppd
    );

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser("For those times when you have a fasta sequence in a specific column of a file");
    parser.add_argument("--inputFile", required=True);    
    parser.add_argument("--titlePresent", action="store_true");
    parser.add_argument("--idColumn", type=int);    
    parser.add_argument("--columnWithSequence", type=int, required=True);    
    parser.add_argument("--kmerLength", type=int, required=True);
    parser.add_argument("--batchSize", type=int, default=100);
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();

    fastaInColumnToKmerIndices(options)
