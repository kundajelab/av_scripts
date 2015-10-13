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

def makeSkeleton(options):
    ofh = fp.getFileHandle(options.inputFile+".py",'w');
    header = """#!/usr/bin/env python
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

""";
    ofh.write(header);
    ofh.write("def "+options.inputFile+"(options):\n\n"); 
    argparseBit = """
if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    
    options = parser.parse_args();
"""
    ofh.write(argparseBit);
    ofh.write("    "+options.inputFile+"(options)\n")
    ofh.close();

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("inputFile");
    options = parser.parse_args();
    makeSkeleton(options);
