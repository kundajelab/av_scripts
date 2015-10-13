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

def shuffleRows(options):
    if (options.titlePresent):
        fileTitle = fp.peekAtFirstLineOfFile(options.inputFile);
    else:
        fileTitle = "" 
    rows = fp.readRowsIntoArr(fp.getFileHandle(options.inputFile),titlePresent=options.titlePresent);
    shuffledRows = util.shuffleArray(rows);
    outputFileName = fp.getFileNameParts(options.inputFile).getFileNameWithTransformation(lambda x: "shuffledRows_"+x);
    ofh = fp.getFileHandle(outputFileName,'w');
    ofh.write(fileTitle);
    for row in rows:
        ofh.write(row+"\n");
    ofh.close(); 

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser("Will read in the input file, generate a random permutation of its rows, and spit it out with the prefix shuffled_");
    parser.add_argument("--inputFile", required=True);
    parser.add_argument("--titlePresent", action="store_true");
    options = parser.parse_args();
    shuffleRows(options);
