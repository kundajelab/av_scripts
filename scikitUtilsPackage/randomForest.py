#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
enhancerScriptsDir = os.environ.get("ENHANCER_SCRIPTS_DIR");
if (enhancerScriptsDir is None):
    raise Exception("Please set environment variable ENHANCER_SCRIPTS_DIR");
sys.path.insert(0,enhancerScriptsDir);
import pathSetter;
from sklearn.multiclass import OneVsRestClassifier;
from sklearn.ensemble import RandomForestClassifier;
from sklearn import preprocessing;
import argparse;
import fileProcessing as fp;
import util;
import generalPurposeScikit;

def getModelInfosArr(options):
    toReturn = [];
    for numTrees in options.numTreesArr:
        toReturn.append(generalPurposeScikit.ModelInfo(RandomForestClassifier(n_estimators=numTrees), "rf-trees"+str(numTrees)));
    return toReturn;

def doClassifier(options):
    trainData, validData, testData = generalPurposeScikit.loadDataFromYaml(options);  
    bestParams = generalPurposeScikit.exploreParams(
                    trainData, validData, testData
                    , getModelInfosArr(options)
                    , options);

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[generalPurposeScikit.getBasicArgparse()]);
    parser.add_argument("--numTreesArr", type=int, nargs='+', default=[10,30,100,300,500,1000]);
    parser.add_argument("--fromEmail", default="rfRunner@stanford.edu");
    options = parser.parse_args();
    if (not options.doNotEmail):
        if (options.jobName is None):
            raise RuntimeError("If going to send emails, must specify a jobName - otherwise, set the doNotEmail flag");
    doClassifier(options);
    

