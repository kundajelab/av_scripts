#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import util;
from synthetic import synthetic as sn;
import argparse;

def do(options):
    outputFileName_core = util.addArguments("EmptyBackground", [
                                                 util.ArgumentToAdd(options.seqLength, "seqLength")
                                                 ,util.ArgumentToAdd(options.numSeqs, "numSeqs")
                                                 ]);
    embedInBackground = sn.EmbedInABackground(
        backgroundGenerator=sn.ZeroOrderBackgroundGenerator(seqLength=options.seqLength) 
        , embedders=[]
    );
    sequenceSet = sn.GenerateSequenceNTimes(embedInBackground, options.numSeqs)
    sn.printSequences(outputFileName_core+".simdata", sequenceSet, includeFasta=True, includeEmbeddings=True);
   
if __name__=="__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--seqLength", type=int, required=True);
    parser.add_argument("--numSeqs", type=int, required=True);
    options = parser.parse_args();
    do(options);     
