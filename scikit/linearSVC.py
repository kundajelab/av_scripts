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
sys.path.insert(0,"/home/avanti/test/lib/python2.6/site-packages");
import pathSetter;
from import_data_methods import load_data_from_yaml_configs;
from sklearn import linear_model;
from sklearn.multiclass import OneVsRestClassifier;
from sklearn import preprocessing;
from sklearn.svm import LinearSVC;
import argparse;
import fileProcessing as fp;
import util;
from accuracyStats import computeConfusionMatrixStats;
from accuracyStats import printConfusionMatrix;
from rocCurve import getMisclassifications_multiLabelWithPredictions;
import numpy as np;
from collections import OrderedDict;
import generalPurposeScikit;

def getModelInfosArr(options):
    toReturn = [];
    for C in options.C:
        toReturn.append(generalPurposeScikit.ModelInfo(LinearSVC(C=C), "svc-C"+str(C)));
    return toReturn;

def doClassifier(options):
    trainData, validData, testData = generalPurposeScikit.loadDataFromYaml(options);  
    bestParams = generalPurposeScikit.exploreParams(
                    trainData, validData, testData
                    , getModelInfosArr(options)
                    , options);

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[generalPurposeScikit.getBasicArgparse()]);
    parser.add_argument("--C", type=float, nargs='+', default=[0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10, 50, 100]);
    parser.add_argument("--fromEmail", default="linearSVC-Runner@stanford.edu");
    options = parser.parse_args();
    if (not options.doNotEmail):
        if (options.jobName is None):
            raise RuntimeError("If going to send emails, must specify a jobName - otherwise, set the doNotEmail flag");
    doClassifier(options);
    

