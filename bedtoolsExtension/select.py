#!/usr/bin/python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;

def select(options):
   
    transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs);
    if (options.outputFile is None):
        prefix = util.addArguments("selected",[util.ArrArgument(options.colsToSelect,"cols")
                                                ,util.CoreFileNameArgument(options.fileWithColumnsToSelect,"colNames")]
                                    );
        options.outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: prefix+"_"+x); 
    outputFileHandle = fp.getFileHandle(options.outputFile, 'w');
    def actionFromTitle(title):
        titleArr = transformation(title);
        #if columns are listed in fileWithColumnsToSelect, append to options.colsToSelect
        if (parser.fileWithColumnsToSelect is not None):
            colNameToIndex = util.valToIndexMap(titleArr);
            colNames = fp.readRowsIntoArr(fp.getFileHandle(fp.fileWithColumnsToSelect));
            for colName in colNames:
                if colName not in colNameToIndex:
                    raise ValueError("Column "+str(colName)+" is not in title");
            colNameIndices = [colNameToIndex[x] for x in colNames];
            options.colsToSelect.extend(colNameIndices);
        
        def action(inp, lineNumber):
            arrToPrint = [inp[x] for x in options.colsToSelect];
            outputFileHandle.write("\t".join(arrToPrint)+"\n");
        action(titleArr, 0); #print out the first line; even if there's no title, this still works.
    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.inputFile)
        ,transformation=transformation
        ,actionFromTitle=actionFromTitle
        ,ignoreInputTitle=True #this isn't problematic because I call 'action' on the first line no matter what
        ,progressUpdate=options.progressUpdate
    );        

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputFile", required=True);
    parser.add_argument("--outputFile");
    parser.add_argument("--colsToSelect", nargs='+', default=[]);
    parser.add_argument("--fileWithColumnsToSelect");
    parser.add_argument("--progressUpdate", type=int, default=10000);   
 
    args = parser.parse_args();
    select(args);  
