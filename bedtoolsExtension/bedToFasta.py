#!/usr/bin/env python
import sys;
import gzip;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;
import parallelProcessing as pp;
import parallelProcessKickerOffer as ppko;
import argparse;

def bedToFasta(options):
    if (options.outputFile is None):
        options.outputFile = fp.getFileNameParts(options.inputBedFile).getFilePathWithTransformation(lambda x: "fastaExtracted_"+x, extension=".fa")
    cmd = "bedtools getfasta -fi "+options.faPath+" -bed "+options.inputBedFile+" -fo "+options.outputFile; 
    util.executeAsSystemCall(cmd);
    util.executeAsSystemCall("gzip "+options.outputFile);

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputBedFile", required=True, help="The file with the bed regions to extract sequences for");
    parser.add_argument("--outputFile", help="Optional; the output file name - autogenerated if not specified");
    parser.add_argument("--faPath", required=True, help="The file with the .fa for the organism");
    options = parser.parse_args();
    bedToFasta(options);
