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
from sets import Set;
import copy;
from collections import OrderedDict;
from collections import namedtuple;

def computeConfusionMatrix(actual, predictions, labelOrdering=None):
    keySet = Set();  
    confusionMatrix = {};
    for i in xrange(0,len(actual)):
        valActual = actual[i];
        valPrediction = predictions[i];
        keySet.add(valActual);
        keySet.add(valPrediction);
        if valActual not in confusionMatrix:
            confusionMatrix[valActual] = {};
        if valPrediction not in confusionMatrix[valActual]:
            confusionMatrix[valActual][valPrediction] = 0;
        confusionMatrix[valActual][valPrediction] += 1;
    keys = sorted(keySet) if labelOrdering is None else labelOrdering;
    #normalise and reorder
    reorderedConfusionMatrix = OrderedDict();
    for valActual in keys:
        if valActual not in confusionMatrix:
            print("Why is "+str(valActual)+" in the predictions but not in the actual?");
            confusionMatrix[valActual] = {};
        reorderedConfusionMatrix[valActual] = OrderedDict();
        for valPrediction in keys: 
            if valPrediction not in confusionMatrix[valActual]:
                confusionMatrix[valActual][valPrediction] = 0;
            reorderedConfusionMatrix[valActual][valPrediction] = confusionMatrix[valActual][valPrediction];
 
    return reorderedConfusionMatrix;
 
def normaliseByRowsAndColumns(theMatrix):
    """
        The matrix is as a dictionary
    """
    sumEachRow = OrderedDict();
    sumEachColumn = OrderedDict();
    for row in theMatrix:
        sumEachRow[row] = 0;
        for col in theMatrix[row]:
            if col not in sumEachColumn:
                sumEachColumn[col] = 0;
            sumEachRow[row] += theMatrix[row][col];
            sumEachColumn[col] += theMatrix[row][col];
    normalisedConfusionMatrix_byRow = copy.deepcopy(theMatrix);
    normalisedConfusionMatrix_byColumn = copy.deepcopy(theMatrix);
    for row in theMatrix:
        for col in theMatrix[row]:
            normalisedConfusionMatrix_byRow[row][col] = 0 if sumEachRow[row] == 0 else theMatrix[row][col]/sumEachRow[row];
            normalisedConfusionMatrix_byColumn[row][col] = 0 if sumEachColumn[col] == 0 else theMatrix[row][col]/sumEachColumn[col];

    return normalisedConfusionMatrix_byRow, normalisedConfusionMatrix_byColumn, sumEachRow, sumEachColumn;

ConfusionMatrixStats = namedtuple('ConfusionMatrixStats', ['confusionMatrix', 'normalisedConfusionMatrix_byRow', 'normalisedConfusionMatrix_byColumn', 'sumEachRow', 'sumEachColumn', 'truePositiveRate', 'trueNegativeRate', 'balancedAccuracy', 'overallAccuracy', 'overallBalancedAccuracy']);
def computeConfusionMatrixStats(actual, predictions, labelOrdering=None):
    confusionMatrix = computeConfusionMatrix(actual, predictions, labelOrdering);
    normalisedConfusionMatrix_byRow, normalisedConfusionMatrix_byColumn, sumEachRow, sumEachColumn = normaliseByRowsAndColumns(confusionMatrix);
    #compute accuracy/balanced accuracy
    #accuracy is everything on the diagonal
    correctPredictions = 0;
    for row in confusionMatrix:
        correctPredictions += confusionMatrix[row][row];
    overallAccuracy = float(correctPredictions)/sum(sumEachRow.values());
    #compute balanced accuracies
    truePositiveRate = OrderedDict();
    trueNegativeRate = OrderedDict();
    balancedAccuracy = OrderedDict();
    totalExamples = len(actual);
    for row in confusionMatrix:
        truePositiveRate[row] = normalisedConfusionMatrix_byRow[row][row];
        trueNegativeRate[row] = (sumEachColumn[row] - confusionMatrix[row][row])/(totalExamples - confusionMatrix[row][row]);
        balancedAccuracy[row] = (truePositiveRate[row] + trueNegativeRate[row])/2;
    overallBalancedAccuracy = 0;
    for row in confusionMatrix:
        overallBalancedAccuracy += (truePositiveRate[row] + trueNegativeRate[row])/2;
    overallBalancedAccuracy = overallBalancedAccuracy / len(confusionMatrix.keys());
    
    return ConfusionMatrixStats(confusionMatrix, normalisedConfusionMatrix_byRow, normalisedConfusionMatrix_byColumn, sumEachRow, sumEachColumn, truePositiveRate, trueNegativeRate, balancedAccuracy, overallAccuracy, overallBalancedAccuracy); 
    
def printConfusionMatrix(matrix, isFloat=False):
    print("\t"+"\t".join(str(x) for x in matrix[matrix.keys()[0]].keys()));
    for row in matrix:
        print(str(row)+"\t"+"\t".join(("{0:.2f}".format(x) if isFloat else str(x)) for x in matrix[row].values()));


    

