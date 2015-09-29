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
import fileProcessing as fp;
import util;
import numpy as np;

DistanceMetrics = util.enum(euclidean="euclidean");

def euclideanDistance(arr1, arr2):
    return np.sqrt(np.sum(np.square(arr1-arr2)));

def getDistanceMetric(distanceMetricName):
    if (distanceMetricName==DistanceMetrics.euclidean):
        return euclideanDistance;
    else:
        raise RuntimeError("Unsupported distance metric: "+distanceMetricName);

def getBestDistanceOverShifts(arr1, arr2, distanceMetric, shiftsToTry, smallerIsBetter=True):
    smallestDistance = util.GetBest_Min() if smallerIsBetter else util.GetBest_Max();
    assert arr1.shape == arr2.shape;
    assert len(arr1.shape)==1;
    lenArr = len(arr1);
    for shift in shiftsToTry: #stride 4 and stuff
        scaleFactor = (float(lenArr)/(lenArr-shift)); #this exists so that shorter seqs don't get an edge for being shorter..but does it penalise shorter seqs unfairly?
        distance1 = distanceMetric(arr1[shift:], arr2[:len(arr2)-shift])*scaleFactor; #this is like sliding the first array backwards relative to the second
        smallestDistance.process(-shift, distance1);
        distance2 = distanceMetric(arr1[:len(arr1)-shift], arr2[shift:])*scaleFactor; #this is like sliding the first array forwards relative to the second
        smallestDistance.process(shift, distance2);
    return smallestDistance.bestObject, smallestDistance.bestVal; 

def distanceMatrix(options):
    the2Dmatrix = fp.read2DMatrix(fp.getFileHandle(options.rawValuesFile),colNamesPresent=options.colNamesPresent,rowNamesPresent=True,contentType=float, contentStartIndex=None,contentEndIndex=None,progressUpdate=None);
    matrixVals = np.array(the2Dmatrix.rows);
    del the2Dmatrix.rows;
    distanceMetric = getDistanceMetric(options.distanceMetric);
    #NOTE
    #must reshape input so that a stride of the appropriate size corresponds to shifting by a base 
    #the way it is for the unrolled inputs, the first index is the base, which is not what you want.
    distanceMatrix = [];
    for (rowName, (i,rowVals)) in zip(the2Dmatrix.rowNames, enumerate(matrixVals)):
        rowToAddToDistanceMatrix = [];
        if (i%options.progressUpdate) == 0:
            print("Done "+str(i));
        for j in range(0,len(matrixVals)): #I realised slicing does fucking copies so I'm not going to slice matrixVals
            if (j < i):
                bestDistance = distanceMatrix[j][i];
            else:
                otherRowName = the2Dmatrix.rowNames[j];
                otherRowVals = matrixVals[j];
                maxShiftDistance = options.numStrides*options.strideLength;
                bestPosition, bestDistance = getBestDistanceOverShifts(rowVals, otherRowVals, distanceMetric, range(0,maxShiftDistance+1, options.strideLength));
            rowToAddToDistanceMatrix.append(bestDistance);
        distanceMatrix.append(rowToAddToDistanceMatrix);
   
    outputFilePrefix = util.addArguments("distanceMatrix", [util.ArgumentToAdd(options.distanceMetric, "metric"), util.ArgumentToAdd(options.numStrides, "numStrides"), util.ArgumentToAdd(options.strideLength, "strideLength")]); 
    outputFileName = fp.getFileNameParts(options.rawValuesFile).getFilePathWithTransformation(lambda x: outputFilePrefix+"_"+x);
    outputFileHandle = fp.getFileHandle(outputFileName,'w');
    fp.writeMatrixToFile(outputFileHandle, distanceMatrix,colNames=the2Dmatrix.rowNames, rowNames=the2Dmatrix.rowNames);  

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--rawValuesFile", required=True);
    parser.add_argument("--colNamesPresent", action="store_true");
    parser.add_argument("--distanceMetric", choices=DistanceMetrics.vals, default=DistanceMetrics.euclidean);
    parser.add_argument("--numStrides", type=int, required=True);
    parser.add_argument("--strideLength", type=int, required=True);
    parser.add_argument("--progressUpdate", type=int, default=1000);
    options = parser.parse_args();

    distanceMatrix(options);
