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
import argparse;
import fileProcessing as fp;
import util;
from accuracyStats import computeConfusionMatrixStats;
from accuracyStats import printConfusionMatrix;
from rocCurve import getMisclassifications_multiLabelWithPredictions;
import numpy as np;

def trainLasso(trainData, alpha, isMultiLabel):
    if (isMultiLabel):
        clf =  linear_model.MultiTaskLasso(alpha=alpha);
    else:
        #ugh this is because I always use a softmax...so
        #it has to look like this for compatibility
        if alpha == 0:
            innerClassifier = linear_model.LinearRegression();
        else:
            innerClassifier = linear_model.Lasso(alpha=alpha);
        #clf = innerClassifier;
        clf = OneVsRestClassifier(innerClassifier);
    clf.fit(trainData.X, np.argmax(np.array(trainData.Y),axis=1));
    #clf.fit(trainData.X, np.array(trainData.Y));
    return clf;

def getPerformance(clf, validData, isMultiLabel, classificationOption, labelOrdering=None):
    predictions = predictLasso(clf, validData, isMultiLabel);
    if (not isinstance(predictions[0], int)): 
        multiLabelAggregatorInfo = getMisclassifications_multiLabelWithPredictions(
            predictions
            , validData.Y
            , 0.5
            , labelOrdering
            , classificationOption);
        theLen = len(multiLabelAggregatorInfo);
        overallBalancedAccuracy = sum([x.balancedMisclassificationRate for x in multiLabelAggregatorInfo])/theLen;
        overallAccuracy = sum([x.misclassificationRate for x in multiLabelAggregatorInfo])/theLen;
    else:
        confusionMatrixStats = computeConfusionMatrixStats(np.argmax(validData.Y, axis=1), predictions, labelOrdering);
        #print("confusion matrix");
        #printConfusionMatrix(confusionMatrixStats.confusionMatrix);
        #print("normalisedConfusionMatrix_byRow");
        #printConfusionMatrix(confusionMatrixStats.normalisedConfusionMatrix_byRow, isFloat=True);
#        print("normalisedConfusionMatrix_byColumn");
#        printConfusionMatrix(confusionMatrixStats.normalisedConfusionMatrix_byColumn, isFloat=True); 
        overallBalancedAccuracy = confusionMatrixStats.overallBalancedAccuracy;
        overallAccuracy = confusionMatrixStats.overallAccuracy;
    return overallBalancedAccuracy, overallAccuracy;
    
def exploreAlphas(trainData, validData, testData, alphas, multiLabelLookup, classificationOption, featureOrdering=None):
    isMultiLabel = multiLabelLookup is not None;
    print("alpha\tbalRate_train\trate_train\tbalRate_valid\trate_valid\tbalRate_test\trate_test\tnonzerFeatures");
    for alpha in alphas:
        clf = trainLasso(trainData, alpha, isMultiLabel);
        labelOrdering = None if multiLabelLookup is None else multiLabelLookup.labelOrdering;
        (balRate_valid, rate_valid) = getPerformance(clf, validData, isMultiLabel, classificationOption, labelOrdering);
        (balRate_test, rate_test) = getPerformance(clf, testData, isMultiLabel, classificationOption, labelOrdering);
        (balRate_train, rate_train) = getPerformance(clf, trainData, isMultiLabel, classificationOption, labelOrdering);
       
        if (featureOrdering is not None):
            for classIndex in range(0,len(clf.coef_)):
                print("Features for class:",classIndex);
                nonzeroFeatures = 0<np.abs(clf.coef_[classIndex]);
                selectedFeatures = featureOrdering[nonzeroFeatures]
                coeffs = clf.coef_[classIndex][nonzeroFeatures];
                print("Num nonzero features",sum(nonzeroFeatures));
                print("\n".join("\t".join(str(x) for x in y) for y in sorted(zip(selectedFeatures,coeffs),key=lambda x: -x[1])));
        nonzeroFeatures = sum(np.sum(np.abs(clf.coef_),axis=0)>0)
        print("\t".join([str(x) for x in [alpha, balRate_train, rate_train, balRate_valid, rate_valid, balRate_test, rate_test, nonzeroFeatures]]));

def predictLasso(clf, data, isMultiLabel):
    prediction = clf.predict(data.X);
    if (not isMultiLabel):
        return prediction;

def doLasso(options):
    featureOrdering = None if options.featureOrdering is None else np.array(fp.readRowsIntoArr(fp.getFileHandle(options.featureOrdering)));
    yamlConfig = load_data_from_yaml_configs(options.yamlConfigs);
    datasetNameToData = yamlConfig.datasetNameToData;
    trainData = datasetNameToData['train'];
    validData = datasetNameToData['valid']; 
    testData = datasetNameToData['test'];
    if not options.doNotScale:
        minMaxScaler = preprocessing.MinMaxScaler();
        minMaxScaler.fit(trainData.X);
        for data in [trainData, validData, testData]:
            data.X = minMaxScaler.transform(data.X);
     
    bestAlpha = exploreAlphas(trainData, validData, testData, options.alphas, yamlConfig.multiLabelLookup, yamlConfig.classificationOption, featureOrdering=featureOrdering);
    #testData = Enhancer(options=options2, data_paths=options.test, multiLabelLookup=multiLabelLookupInfo);

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--yamlConfigs", nargs="+", required=True);
    parser.add_argument("--alphas", type=float, nargs='+', default=[0, 0.00001, 0.0001, 0.0003, 0.0007
                                , 0.001, 0.00125, 0.0015, 0.00175, 0.002, 0.00225, 0.0025, 0.00275, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009
                                , 0.01, 0.02]);
    parser.add_argument("--doNotScale", action="store_true");
    parser.add_argument("--featureOrdering");
    
    args = parser.parse_args();
    doLasso(args);
    

