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

def getDistanceMetric(distanceMetricName):
    if (distanceMetricName==DistanceMetrics.euclidean):
        return euclideanDistance;
    else:
        raise RuntimeError("Unsupported distance metric: "+distanceMetricName);

def euclideanDistance(rowVals, matrixVals):
    assert len(matrixVals.shape)==2;
    assert rowVals.shape[1]==matrixVals.shape[1];
    assert len(rowVals.shape)==2;
    assert rowVals.shape[0]==1;
    return np.sqrt(np.sum(np.square(matrixVals-rowVals),axis=1))
    return np.sqrt(np.sum(np.square(arr1-arr2)));

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
        shiftsByDistances = []; #np.zeros(((options.numStrides+1)*2, len(the2Dmatrix.rowNames))); #options.numStrides+1 because there's also the zero shift...which will be repeated twice but whatever
        maxShiftDistance = options.numStrides*options.strideLength;
        for (shiftIdx, shift) in enumerate(range(0,maxShiftDistance+1, options.strideLength)):
            #shift forward
            matrixValsWithShift = matrixVals[:, shift:];
            rowValsWithShift = rowVals[None, :len(rowVals)-shift];
            distances = distanceMetric(rowValsWithShift, matrixValsWithShift); 
            shiftsByDistances.append(distances);
            #shift backwards
            matrixValsWithShift = matrixVals[:, :len(rowVals)-shift];
            rowValsWithShift = rowVals[None, shift:];
            distances = distanceMetric(rowValsWithShift, matrixValsWithShift); 
            scaleFactor = (float(len(rowVals))/(len(rowVals)-shift)); #this exists so that shorter seqs don't get an edge for being shorter..but does it penalise shorter seqs unfairly?
            shiftsByDistances.append(distances*scaleFactor);
        bestDistances = np.min(np.array(shiftsByDistances), axis=0);
        distanceMatrix.append(bestDistances);
   
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
