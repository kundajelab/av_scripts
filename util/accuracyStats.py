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
import sklearn.metrics;
import numpy as np;

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

ConfusionMatrixStats = namedtuple('ConfusionMatrixStats', ['confusionMatrix', 'normalisedConfusionMatrix_byRow', 'normalisedConfusionMatrix_byColumn', 'sumEachRow', 'sumEachColumn', 'truePositiveRate', 'trueNegativeRate', 'balancedAccuracy', 'overallAccuracy', 'overallBalancedAccuracy', "majorityClass"]);
def computeConfusionMatrixStats(actual, predictions, labelOrdering=None):
    confusionMatrix = sklearn.metrics.confusion_matrix(actual, predictions);
    sumEachRow=np.sum(confusionMatrix,axis=1);
    sumEachColumn=np.sum(confusionMatrix,axis=0);
    normalisedConfusionMatrix_byRow = confusionMatrix/(sumEachRow[:,None] + 0.000000000000000000000000000000000000000000000000000000000000000001);
    normalisedConfusionMatrix_byColumn = confusionMatrix/(sumEachColumn[None,:]+ 0.00000000000000000000000000000000000000000000000000000000000001);
    #compute accuracy/balanced accuracy
    #accuracy is everything on the diagonal
    correctPredictions = 0;
    for row in xrange(len(confusionMatrix)):
        correctPredictions += confusionMatrix[row,row];
    totalExamples = sum(sumEachRow);
    overallAccuracy = 0.0 if totalExamples==0 else float(correctPredictions)/totalExamples;
    majorityClass = 0.0 if totalExamples==0 else float(max(sumEachRow))/totalExamples;
    #compute balanced accuracies
    truePositiveRate = OrderedDict();
    trueNegativeRate = OrderedDict();
    balancedAccuracy = OrderedDict();
    totalExamples = len(actual);
    for row in xrange(len(confusionMatrix)):
        truePositiveRate[row] = normalisedConfusionMatrix_byRow[row,row];
        trueNegativeRate[row] = (totalExamples - sumEachColumn[row])/(totalExamples - sumEachRow[row]) if (totalExamples-sumEachRow[row]) > 0 else 0.0;
        balancedAccuracy[row] = (truePositiveRate[row] + trueNegativeRate[row])/2;
    overallBalancedAccuracy = 0;
    for row in xrange(len(confusionMatrix)):
        overallBalancedAccuracy += balancedAccuracy[row];
    overallBalancedAccuracy = overallBalancedAccuracy / len(confusionMatrix);
    
    return ConfusionMatrixStats(confusionMatrix, normalisedConfusionMatrix_byRow, normalisedConfusionMatrix_byColumn, sumEachRow, sumEachColumn, truePositiveRate, trueNegativeRate, balancedAccuracy, overallAccuracy, overallBalancedAccuracy, majorityClass); 
    
def printConfusionMatrix(matrix, isFloat=False):
    print("\t"+"\t".join(str(x) for x in matrix[matrix.keys()[0]].keys()));
    for row in matrix:
        print(str(row)+"\t"+"\t".join(("{0:.2f}".format(x) if isFloat else str(x)) for x in matrix[row].values()));


    

