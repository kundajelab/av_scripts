#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;

def concatenateFilesThatHaveTitles(options):
    for (i,fileName) in enumerate(options.filesWithTitleToConcat):
        print("on file",fileName);
        if (i == 0):
            os.system("cp "+fileName+" "+options.outputFile);
        else:
            os.system("perl -pe '$_ = (($. == 1) ? \"\" : $_)' "+fileName+" >> "+options.outputFile);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--filesWithTitleToConcat", nargs="+", required=True);
    parser.add_argument("--outputFile", required=True);
    options = parser.parse_args();
    concatenateFilesThatHaveTitles(options);
