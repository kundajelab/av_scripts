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

def summariseFeatureStats(options):
    
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "summaryStats_"+("revComp_" if options.revComp else "")+str(x), extension=".txt");

    featuresWrapper = util.VariableWrapper(None); 
    sumWrapper = util.VariableWrapper(None);
    sumSquaresWrapper = util.VariableWrapper(None);
    minWrapper = util.VariableWrapper(None);
    maxWrapper = util.VariableWrapper(None);
    totalRegionsWrapper = util.VariableWrapper(0);
    if (options.revComp):
        reverseComplementIndexMappingWrapper = util.VariableWrapper(None);
    def action(inp, lineNumber):
        if (lineNumber == 1):
            featuresWrapper.var = inp[1:];
            sumWrapper.var = np.zeros(len(inp)-1);
            sumSquaresWrapper.var = np.zeros(len(inp)-1);
            if options.revComp:
                kmerToIndex = dict((x[1],x[0]) for x in enumerate(featuresWrapper.var));
                reverseComplementIndexMappingWrapper.var = dict([(x[0], kmerToIndex[util.reverseComplement(x[1])]) for x in enumerate(featuresWrapper.var)]);
        else:
            totalRegionsWrapper.var += 1;
            countsArr = np.array([int(x) for x in inp[1:]]); #TODO: generalise to not-just-ints
            if (options.revComp):
                revCompKmerCounts = countsArr.copy();
                for i,kmerCount in enumerate(countsArr):
                    revCompKmerCounts[reverseComplementIndexMappingWrapper.var[i]] += kmerCount;
                countsArr=revCompKmerCounts;
            sumWrapper.var += countsArr;
            sumSquaresWrapper.var += np.square(countsArr);
            if (totalRegionsWrapper.var == 1):
                minWrapper.var = countsArr.copy()
                maxWrapper.var = countsArr.copy()
            minWrapper.var = np.minimum(minWrapper.var, countsArr)
            maxWrapper.var = np.maximum(maxWrapper.var, countsArr) 
        
    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.inputFile)
        ,action=action
        ,transformation=fp.defaultTabSeppd
        ,progressUpdate=options.progressUpdate
    );

    mean = sumWrapper.var/float(totalRegionsWrapper.var);
    sdev=np.sqrt((sumSquaresWrapper.var/float(totalRegionsWrapper.var)) - mean**2)
    outputFileHandle = fp.getFileHandle(outputFile, 'w');
    outputFileHandle.write("feature\tmean\tsdev\tmin\tmax\n");
    for (feature, theMean, theSdev, theMin, theMax) in zip(featuresWrapper.var, mean, sdev, minWrapper.var, maxWrapper.var):
        outputFileHandle.write(feature+"\t"+str(theMean)+"\t"+str(theSdev)+"\t"+str(theMin)+"\t"+str(theMax)+"\n");

    outputFileHandle.close();

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputFile", required=True, help="Assumed to be a titled file where first col is id and remaining cols are features"); 
    parser.add_argument("--revComp", action="store_true", help="If specified, assumes features are kmers and reverse complements things");
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();
    summariseFeatureStats(options)
