#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import argparse;
from minMemStatsComp import MeanFinder, SdevFinder, CountNonZeros, MinFinder, MaxFinder;    


def getActionFromTitle(options, memStatsComputerInitialisers):
    lineProcessing = util.chainFunctions(fp.trimNewline, fp.splitByTabs);

    memStatsComputers = [];
    def actionFromTitle(title):
        title = lineProcessing(title);
        #relevantIndices are the column indices that we want to compute stats for
        relevantIndices = util.invertIndices(options.colsToIgnore, range(len(title)));
        for relevantIndex in relevantIndices:
            colName = title[relevantIndex];
            memStatsComputers_forColumn = [];
            for memStatsComputerInitialiser in memStatsComputerInitialisers:
                memStatsComputers_forColumn.append(memStatsComputerInitialiser(colName));
            memStatsComputers.append(memStatsComputers_forColumn);
        mod = 1;
        if (options.subsample is not None):
            print "Subsampling set to: "+str(options.subsample);
            mod = int(float(1)/(options.subsample));
            print "We are sampling every "+str(mod)+"th line";
        def action(inp, lineNumber):
            #if subsample is enabled, only consider a subset of the lines.
            if ((options.subsample is not None) or lineNumber%mod == 0): 
                for computerIdx,inpIdx in enumerate(relevantIndices):
                    memStatsComputers_forColumn = memStatsComputers[computerIdx];
                    for memStatsComputer_forColumn in memStatsComputers_forColumn:
                        memStatsComputer_forColumn.process(float(inp[inpIdx]));
   
        return action; 
    return actionFromTitle,memStatsComputers; 

def computeStatsForColumns(options):
    memStatsComputerInitialisers = []; #functions that take as input a name and return the stats computer 
    if (options.mean):
        memStatsComputerInitialisers.append(lambda name: MeanFinder(name));
    if (options.sdev):
        memStatsComputerInitialisers.append(lambda name: SdevFinder(name));
    if (options.nonzeroVals):
        memStatsComputerInitialisers.append(lambda name: CountNonZeros(name, percentIncidence=True));  
    if (options.minMax):
        memStatsComputerInitialisers.append(lambda name: MinFinder(name));
        memStatsComputerInitialisers.append(lambda name: MaxFinder(name));

    actionFromTitle, memStatsComputers = getActionFromTitle(options, memStatsComputerInitialisers);
    fp.performActionOnEachLineOfFile(
        fp.getFileHandle(options.inputFile)
        , transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs)
        , actionFromTitle = actionFromTitle
        , ignoreInputTitle = True #title present
        , progressUpdate = options.progressUpdate
    );
    #call finalise!
    for memStatsComputer_forColumn in memStatsComputers:
        for memStatsComputer in memStatsComputer_forColumn:
            memStatsComputer.finalise();
    return memStatsComputers;

def computeStatsForColumnsAndWriteOutput(options, sep="\t"):
    memStatsComputers = computeStatsForColumns(options); 
    if (options.outputFile is None): #generate an output file name
        prefix = "statsComputed";
        if (options.subsample is not None):
            prefix += "_"+str(options.subsample);
        for attribute in ('mean', 'sdev', 'nonzeroVals'):
            if getattr(options, attribute) == True:
                prefix += "_"+attribute;
        options.outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: prefix+"_"+x, extension=".tsv");

    outputFileHandle = fp.getFileHandle(options.outputFile, 'w');
    
    lineNumber = 0;
    for memStatsComputers_forCol in memStatsComputers:
        lineNumber += 1;
        if (lineNumber == 1): #spit out title
            titleArr = ["featureName"];
            for memStatsComputer in memStatsComputers_forCol:
               titleArr.append(memStatsComputer.statsComputerType);
            outputFileHandle.write(sep.join(titleArr)+"\n");
        outputLine = [];
        outputLine.append(memStatsComputers_forCol[0].name);
        outputLine.extend([str(x.getVal()) for x in memStatsComputers_forCol]);
        outputFileHandle.write(sep.join(outputLine)+"\n");

    outputFileHandle.close();


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Assumes titles are present");
    parser.add_argument("--inputFile", required=True);
    parser.add_argument("--outputFile");
    colsToIgnoreDefault = [0,1];
    parser.add_argument("--colsToIgnore", type=int, nargs='+', default=colsToIgnoreDefault, help="Wont compute stats for these columns. Default: "+str(colsToIgnoreDefault));
    parser.add_argument("--mean", action="store_true", help="Include this flag to find the mean for the columns");
    parser.add_argument("--sdev", action="store_true", help="Include to find standard dev for the columns");
    parser.add_argument("--minMax", action="store_true", help="Include this flag to find the min and max for the columns");
    parser.add_argument("--nonzeroVals", action="store_true", help="Include flag to find all vals that are nonzero");
    parser.add_argument("--subsample", type=float);
    parser.add_argument("--progressUpdate", type=int, default=10000);
    args = parser.parse_args();
    computeStatsForColumnsAndWriteOutput(args);


