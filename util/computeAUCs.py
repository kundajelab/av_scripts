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

def computeAUCs(options):
    trueLabels = [int(x) for x in fp.readColIntoArr(fp.getFileHandle(options.trueLabelsFile), col=options.trueLabelsCol)];
    predictedScores = [float(x) for x in fp.readColIntoArr(fp.getFileHandle(options.predictedScoresFile), col=options.predictedScoresCol)]
    pngFile = fp.getFileNameParts(options.predictedScoresFile).getFilePathWithTransformation(lambda x: "auPRC_"+x,extension=".png");
    print(util.auPRC(trueLabels, predictedScores, pngFile));

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--trueLabelsFile", required=True);
    parser.add_argument("--trueLabelsCol", type=int, required=True);
    parser.add_argument("--predictedScoresFile", required=True);    
    parser.add_argument("--predictedScoresCol", type=int, required=True);    
    options = parser.parse_args();
    computeAUCs(options)
