#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import argparse;

GENERATION_OPTION = util.enum(zeroOrderMarkov="zeroOrderMarkov");

def generateString_zeroOrderMarkov(length, discreteDistribution=util.DEFAULT_DISCRETE_DISTRIBUTION):
    """
        discreteDistribution: instance of util.DiscreteDistribution
    """
    sampledArr = util.sampleNinstancesFromDiscreteDistribution(length, discreteDistribution);
    return "".join(sampledArr);

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--generationOption", default=GENERATION_OPTION.zeroOrderMarkov, choices=GENERATION_OPTION.vals);
    parser.add_argument("--N", type=int, required=True);
    parser.add_argument("--M", type=int, required=True);
    options = parser.parse_args(); 

    outputFileName = options.generationOption+"_numSeq"+str(options.N)+"_seqLen"+str(options.M)+".txt";
 
    outputFileHandle = open(outputFileName, 'w');
    outputFileHandle.write("id\tsequence\n");
    for i in xrange(options.N):
        outputFileHandle.write("zeroOrder_seq"+str(i)+"\t"+generateString_zeroOrderMarkov(length=options.M)+"\n");
    outputFileHandle.close();

     

