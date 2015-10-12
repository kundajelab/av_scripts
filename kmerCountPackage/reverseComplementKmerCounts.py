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

def reverseComplementKmerCounts(options):
    
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "revComp_"+str(x));
    outputFileHandle = fp.getFileHandle(outputFile, 'w');    

    reverseComplementIndexMappingWrapper = util.VariableWrapper(None);
    def action(inp, lineNumber):
        if (lineNumber==1):
            outputFileHandle.write("\t".join(inp));
            outputFileHandle.write("\n");
            kmerOrdering = inp[1:];
            kmerToIndex = dict((x[1],x[0]) for x in enumerate(kmerOrdering));
            reverseComplementIndexMappingWrapper.var = dict([(x[0], kmerToIndex[util.reverseComplement(x[1])]) for x in enumerate(kmerOrdering)]);
        else:
            theId = inp[0];
            kmerCounts = [int(x) for x in inp[1:]]
            revCompKmerCounts = kmerCounts[:]; #slicing makes a copy
            for i,kmerCount in enumerate(kmerCounts):
                revCompKmerCounts[reverseComplementIndexMappingWrapper.var[i]] += kmerCount;
            outputFileHandle.write(theId);
            outputFileHandle.write("\t");
            outputFileHandle.write("\t".join(str(x) for x in revCompKmerCounts));
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
    parser.add_argument("--inputFile", required=True, help="Expects as input a file generated by computeKmerCounts.py"); 
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();
    reverseComplementKmerCounts(options)
