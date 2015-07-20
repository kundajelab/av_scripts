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
import fileProcessing as fp;

def rowNormalise(options):
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "rowNormalised_"+x);
    outputFileHandle = fp.getFileHandle(outputFile,'w');
    def action(inp,lineNumber):
        if (lineNumber == 1): #assume there is a title row and row names
            outputFileHandle.write("\t".join(inp)+"\n");
        else:
            rowName = inp[0];
            floatRow = [float(x) for x in inp[1:]];
            rowSum = sum(floatRow);
            floatRow = [x/rowSum for x in floatRow];
            outputFileHandle.write(rowName+"\t"+"\t".join(str(x) for x in floatRow)+"\n");
    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.inputFile)
        ,action=action
        ,transformation=fp.defaultTabSeppd
    );
    outputFileHandle.close();

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser("Assumes there is a title row and that the rows are named. Will normalise the rows by their sum");
    options = parser.add_argument("--inputFile", required=True);
    options = parser.parse_args(); 
    rowNormalise(options);
