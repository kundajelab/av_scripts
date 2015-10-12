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
import seqToKmerIds;

def computeKmerCounts(options):
    
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "kmerCountsPerSeq_"+str(x));
    
    kmerOrdering = seqToKmerIds.getKmerOrdering(options.kmerLength);
    kmerOrderingWithoutNs = [x for x in kmerOrdering if 'N' not in x];
    kmerToIndexMappingWithoutNs = dict((x[1], x[0]) for x in enumerate(kmerOrderingWithoutNs))
    indexRemapping = dict([(x[0], kmerToIndexMappingWithoutNs[kmerOrdering[x[0]]]) for x in enumerate(kmerOrdering) if 'N' not in x[1]]);
    outputFileHandle = fp.getFileHandle(outputFile, 'w')

    #write the title
    outputFileHandle.write("id");
    outputFileHandle.write("\t");
    outputFileHandle.write("\t".join(kmerOrderingWithoutNs));
    outputFileHandle.write("\n");

    def action(inp, lineNumber):
        theId = inp[0];
        kmerIds = [int(x) for x in inp[1].split()];
        kmerIdsWithoutNs = [indexRemapping[x] for x in kmerIds if x in indexRemapping];
        toPrint = [0]*len(kmerOrderingWithoutNs);
        for kmerId in kmerIdsWithoutNs:
            toPrint[kmerId] += 1;
        outputFileHandle.write(theId);
        outputFileHandle.write("\t");
        outputFileHandle.write("\t".join(str(x) for x in toPrint));
        outputFileHandle.write("\n");

    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.inputFile)
        ,action=action
        ,transformation=fp.defaultTabSeppd
        ,progressUpdate=options.progressUpdate
    );
    outputFileHandle.close();

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputFile", required=True, help="Assumed to be a file of kmer ids produced by fastaToKmerIndices.py or something like that"); 
    parser.add_argument("--kmerLength", type=int);
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();
    computeKmerCounts(options)
