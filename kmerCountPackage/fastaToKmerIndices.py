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
import profileSequences;
from kmerCountPackage import countKmers;

def countKmersInFasta(options):
    fastaIterator = fp.FastaIterator(options.fastaInput);
    for (key, sequence) in fastaIterator:
        kmerCounts = countKmers.getKmerCounts(sequence, );  

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--fastaInput", required=True);    
    parser.add_argument("--kmerLength", type=int, required=True);
    options = parser.parse_args();
    


    countKmersInFasta(options)
