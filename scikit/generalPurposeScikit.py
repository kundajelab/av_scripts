#!/usr/bin/env python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
from importDataPackage import importData;
from sklearn import preprocessing;
from collections import OrderedDict;
import argparse;
import fileProcessing as fp;
import util;
from accuracyStats import computeConfusionMatrixStats;
from accuracyStats import printConfusionMatrix;
import numpy as np;

class SingleClassificationRateTracker(object):
    def __init__(self,label):
        self.label = label;
        self.positives = 0;
        self.negatives = 0;
        self.truePositives = 0;
        self.trueNegatives = 0;

    def update(self,prediction,correctAnswer,threshold=None):
        """
            When prediction is a value from 0 to 1.
        """
        #assert (prediction >= 0 and prediction <= 1);
        assert (correctAnswer == 0 or correctAnswer == 1);
        if (threshold==None):
            assert (prediction == 0 or prediction == 1);      
        if (correctAnswer == 0):
            self.negatives += 1;
            if ((threshold == None and prediction == 0) or (threshold != None and prediction < threshold)):
                self.trueNegatives += 1;
        if (correctAnswer == 1):
            self.positives += 1;
            if ((threshold == None and prediction == 1) or (threshold != None and prediction >= threshold)):
                self.truePositives += 1;

def getMisclassifications_multiLabelWithPredictions(rawPredictions, yCorrect, threshold, labelOrdering):
    if labelOrdering == None:
        labelOrdering=range(len(rawPredictions[0]));
    #initialise multilabel misclassification data counters for each of the categories.
    multiLabelAggregatorInfo = [SingleClassificationRateTracker(x) for x in labelOrdering]; 
    overallAggregator = SingleClassificationRateTracker("overall");
    for (predictionIdx,prediction) in enumerate(rawPredictions):
        for (labelIdx,labelPredicted) in enumerate(prediction):
            correctPrediction = yCorrect[predictionIdx][labelIdx];
            multiLabelAggregatorInfo[labelIdx].update(labelPredicted, correctPrediction,threshold);
            overallAggregator.update(labelPredicted, correctPrediction, threshold);
    overallAggregator.finalise();
    for aggregator in multiLabelAggregatorInfo:
        aggregator.finalise();
    multiLabelAggregatorInfo = sorted(multiLabelAggregatorInfo, key=lambda x: x.balancedMisclassificationRate);
    toReturn = [overallAggregator];
    toReturn.extend(multiLabelAggregatorInfo);
    return toReturn;

class ModelInfo(object):
    def __init__(self, model, modelName):
        self.model = model;
        self.modelName = modelName;
        
def trainModel(clf, trainData):
    if (trainData.Y.shape[1] == 1): #if is column vector, make a 1-d array
        clf.fit(trainData.X, np.ravel(trainData.Y));
    else:
        clf.fit(trainData.X, np.array(trainData.Y));

def getPerformance(clf, data, labelOrdering=None, verbose=False):
    predictions = clf.predict(data.X);
    if (not isinstance(predictions[0], int)): 
        multiLabelAggregatorInfo = getMisclassifications_multiLabelWithPredictions(
            predictions
            , data.Y
            , 0.5
            , labelOrdering
            , classificationOption);
        theLen = len(multiLabelAggregatorInfo);
        overallBalancedAccuracy = sum([(1-x.balancedMisclassificationRate) for x in multiLabelAggregatorInfo])/theLen;
        overallAccuracy = sum([(1-x.misclassificationRate) for x in multiLabelAggregatorInfo])/theLen;
        majorityClassAccuracy = sum([1-x.majorityClassMisclassificationRate for x in multiLabelAggregatorInfo])/theLen;
    else:
        confusionMatrixStats = computeConfusionMatrixStats(data.Y, predictions, labelOrdering);
        if (verbose):
            print("confusion matrix");
            printConfusionMatrix(confusionMatrixStats.confusionMatrix);
            print("normalisedConfusionMatrix_byRow");
            printConfusionMatrix(confusionMatrixStats.normalisedConfusionMatrix_byRow, isFloat=True);
            #printConfusionMatrix(confusionMatrixStats.normalisedConfusionMatrix_byColumn, isFloat=True); 
        overallBalancedAccuracy = confusionMatrixStats.overallBalancedAccuracy;
        overallAccuracy = confusionMatrixStats.overallAccuracy;
        majorityClassAccuracy = confusionMatrixStats.majorityClass;
    return overallBalancedAccuracy, overallAccuracy, majorityClassAccuracy;
    
def exploreParams(trainData, validData, testData, numTreesArr, multiLabelLookup, classificationOption, options):
    summaryValuesForEachParameter = OrderedDict();
    emailContent = "";
    dp = 5;
    for (iteration, numTrees) in enumerate(numTreesArr):
        summaryValues = OrderedDict();
        clf = trainModel(trainData, numTrees);
        #print("\n".join(str(x) for x in clf.feature_importances_));
        labelOrdering = trainData.labelNames;
        for (datasetLabel, dataset) in [('trn',trainData), ('val', validData), ('tes', testData)]:
            (balRate, overallRate, majorityClassRate) = getPerformance(clf, dataset, labelOrdering, verbose=options.verbose);
            summaryValues[datasetLabel+"_bal"] = round(balRate,dp);
            summaryValues[datasetLabel+"_acc"] = round(overallRate,dp);
            summaryValues[datasetLabel+"_maj"] = round(majorityClassRate,dp);
        summaryValuesForEachParameter[numTrees] = summaryValues; 
        if (iteration==0):
            titleEntries = summaryValues.keys();
            title = "numTree"+"\t"+"\t".join(titleEntries)
            print(title);
        row = str(numTrees)+"\t"+"\t".join([str(x) for x in summaryValues.values()]);
        print(row);
        if (not options.doNotEmail):
            try:
                emailContent = "numTrees\t"+"\t".join(str(x) for x in summaryValuesForEachParameter.keys())+"\n";
                footer = "\n".join(options.yamlConfigs);
                for stat in titleEntries:
                    rowToAdd = str(stat)+"\t"+"\t".join(str(summaryValuesForEachParameter[x][stat]) for x in summaryValuesForEachParameter.keys())+"\n";
                    emailContent+=rowToAdd;
                util.sendEmail(options.address, options.fromEmail, "numTrees"+str(numTrees)+", "+options.jobName, emailContent+"\n"+footer); 
            except:
                print("Could not send email");
                pass;
    
def exploreParams(trainData, validData, testData, modelInfos, options):
    summaryValuesForEachParameter = OrderedDict();
    emailContent = "";
    dp = 5;
    for (iteration, modelInfo) in enumerate(modelInfos):
        summaryValues = OrderedDict();
        clf = modelInfo.model;
        trainModel(clf, trainData);
        #print("\n".join(str(x) for x in clf.feature_importances_));
        labelOrdering = trainData.labelNames;
        for (datasetLabel, dataset) in [('trn',trainData), ('val', validData), ('tes', testData)]:
            (balRate, overallRate, majorityClassRate) = getPerformance(clf, dataset, labelOrdering, verbose=options.verbose);
            summaryValues[datasetLabel+"_bal"] = round(balRate,dp);
            summaryValues[datasetLabel+"_acc"] = round(overallRate,dp);
            summaryValues[datasetLabel+"_maj"] = round(majorityClassRate,dp);
        summaryValuesForEachParameter[modelInfo.modelName] = summaryValues; 
        if (iteration==0):
            titleEntries = summaryValues.keys();
            title = "name-"+"\t"+"\t".join(titleEntries)
            print(title);
        row = str(modelInfo.modelName)+"\t"+"\t".join([str(x) for x in summaryValues.values()]);
        print(row);
        if (not options.doNotEmail):
            try:
                emailContent = "name\t"+"\t".join(str(x) for x in summaryValuesForEachParameter.keys())+"\n";
                footer = "\n".join(options.yamlConfigs);
                for stat in titleEntries:
                    rowToAdd = str(stat)+"\t"+"\t".join(str(summaryValuesForEachParameter[x][stat]) for x in summaryValuesForEachParameter.keys())+"\n";
                    emailContent+=rowToAdd;
                util.sendEmail(options.address, options.fromEmail, "name-"+str(modelInfo.modelName)+", "+options.jobName, emailContent+"\n"+footer); 
            except:
                print("Could not send email");
                pass;

def loadDataFromYaml(options):
    """
        Expect: options.yamlConfigs
                options.doNotScale
    """
    import yaml;
    splitNameToInputData = importData.getSplitNameToInputDataFromSeriesOfYamls([yaml.load(fp.getFileHandle(x)) for x in options.yamlConfigs]);
    trainData = splitNameToInputData['train'];
    validData = splitNameToInputData['valid']; 
    testData = splitNameToInputData['test'];
    if not options.doNotScale:
        for data in [trainData, validData, testData]:
            data.X = preprocessing.scale(data.X);
    return trainData, validData, testData;

def obtainInputData(data_path, classificationOption, multiLabelLookup, yLookup):
    ids,categories,outcomes,predictors,labelRepresentationCounters = load_data(
        data_path, classificationOption, multiLabelLookup, yLookup);
    return InputData(ids,categories,outcomes,predictors,labelRepresentationCounters);

def getBasicArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--yamlConfigs", nargs="+", required=True);
    parser.add_argument("--doNotScale", action="store_true");
    parser.add_argument("--doNotEmail", action="store_true");
    parser.add_argument("--address", default="avanti@stanford.edu"); 
    parser.add_argument("--jobName");
    parser.add_argument("--verbose", action="store_true");
    return parser;
