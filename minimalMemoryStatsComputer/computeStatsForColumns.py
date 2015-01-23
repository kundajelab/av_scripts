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
from minimalMemoryStatsComputer import MeanFinder, SdevFinder, CountNonZeros;    


def getActionFromTitle(options, memStatsComputerInitialisers):
    lineProcessing = util.chainFunctions(fp.trimNewline, fp.splitByTabs);

    def actionFromTitle(title):
        title = lineProcessing(title);
        memStatsComputers = [];
        colsToIgnoreDefaultHash = dict((x,1) for x in colsToIgnoreDefault);
        relevantIndices = [x for x in range(0,len(title)) if x in colsToIgnoreDefaultHash];
        for relevantIndex in relevantIndices:
            colName = title[relevantIndex];
            memStatsComputers_forColumn = [];
            for memStatsComputerInitialiser in memStatsComputerInitialisers:
                memStatsComputers_forColumn.append(memStatsComputerInitialiser(colName));
            memStatsComputers.append(memStatsComputers_forColumn);
        def action(inp, lineNumber):
            for relevantIndex in relevantIndices:
                memStatsComputers_forColumn = memStatsComputers[relevantIndex];
                for memStatsComputer_forColumn in memStatsComputers_forColumn:
                    memStatsComputer_forColumn.process(inp[relevantIndex]);
    
    return actionFromTitle,memStatsComputers;
            
            

def computeStatsForColumns(options):
    memStatsComputerInitialisers = []; #functions that take as input a name and return the stats computer 
    if (options.mean):
        memStatsComputerInitialisers.append(lambda name: MeanFinder(name));
    if (options.sdev):
        memStatsComputerInitialisers.append(lambda name: SdevFinder(name));
    if (options.nonzeroVals):
        memStatsComputerInitialisers.append(lambda name: CountNonZeros(name));  

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Assumes titles are present");
    parser.add_argument("--inputFile", required=True);
    colsToIgnoreDefault = [0,1];
    parser.add_argument("--colsToIgnore", type=int, nargs='+', default=colsToIgnoreDefault, help="Wont compute stats for these columns. Default: "+str(colsToIgnoreDefault));
    parser.add_argument("--mean", action="store_true", help="Include this flag to find the mean for the columns");
    parser.add_argument("--sdev", action="store_true", help="Include to find standard dev for the columns");
    parser.add_argument("--nonzeroVals", action="store_true", help="Include flag to find all vals that are nonzero");
    args = parser.parse_args();
    computeStatsForColumns(args);




