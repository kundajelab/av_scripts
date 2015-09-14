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
        distance = distanceMetric(arr1[shift:], arr2[:len(arr2)-shift])*(lenArr/(lenArr-shift));
        smallestDistance.process(shift, distance);
   return smallestDistance.bestObject, smallestDistance.bestVal; 

def distanceMatrix(options):
    the2Dmatrix = fp.read2DMatrix(fileHandle,colNamesPresent=False,rowNamesPresent=True,contentType=float, contentStartIndex=None,contentEndIndex=None,progressUpdate=None);
    matrixVals = np.array(the2Dmatrix.rows);
    del the2Dmatrix.rows;
    #NOTE
    #must reshape input so that a stride of the appropriate size corresponds to the appropriate thing 
    #the way it is for the unrolled inputs, it's row-major which is not what I want
    for (rowName, (i,rowVals)) in zip(the2Dmatrix.rowNames, enumerate(matrixVals)):
        for j in range(i,len(matrixVals)): #I realised slicing does fucking copies so I'm not going to slice matrixVals
            otherRowName = the2Dmatrix.rowNames[j];
            otherRowVals = matrixVals[j];
            bestDistance = getBestDistanceOverShifts(rowVals, otherRowVals, 


if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--rawValues", required=True);
    parser.add_argument("--distanceMetric", choices=DistanceMetrics.vals, required=True);
    parser.add_argument("--shiftWindow", type=int, required=True);
    parser.add_argument("--shiftStride", type=int, required=True);
    options = parser.parse_args();

    distanceMatrix(options);
