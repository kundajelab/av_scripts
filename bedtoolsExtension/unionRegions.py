#!/usr/bin/env python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;
from collections import OrderedDict;

def unionRegions(options):
    regions = OrderedDict();
    outputFileHandle=fp.getFileHandle(options.unifiedRegionsOutputFile,'w');
    for fileName in options.filesToMerge:
        fileHandle = fp.getFileHandle(fileName);
        def action(inp, lineNumber):
            chrom=inp[0];
            start=inp[1];
            end=inp[2];
            regionId=util.makeChromStartEnd(chrom,start,end);
            if (regionId not in regions):
                outputFileHandle.write(chrom+"\t"+start+"\t"+end+"\n");
                regions[regionId]=1;
        fp.performActionOnEachLineOfFile(
            fileHandle=fileHandle
            ,action=action
            ,transformation=fp.defaultTabSeppd
        );
    outputFileHandle.close();

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--filesToMerge", nargs="+");
    parser.add_argument("--unifiedRegionsOutputFile",required=True);
    options = parser.parse_args();
    unionRegions(options);  
