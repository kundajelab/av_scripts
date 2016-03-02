from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to av_scripts");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import numpy as np;
from scipy import stats

def grubbsTest_max_findOutliers_unsortedArr(arr, confidenceLevel):
    #returns the indices of the outliers
    sortedEnumerated = sorted(enumerate(arr), key=lambda x: x[1]);
    valuesOnly = [x[1] for x in sortedEnumerated];
    indicesOnly = [x[0] for x in sortedEnumerated];
    numOutliers = grubbsTest_max_findOutliers_sortedArr(valuesOnly, confidenceLevel);
    return indicesOnly[len(arr)-numOutliers:len(arr)];

def grubbsTest_max_findOutliers_sortedArr(arr, confidenceLevel):
    arr = util.npArrayIfList(arr);
    #will return the number of upper-level outliers
    numOutliers = 0;
    isOutlier=True;
    while isOutlier:
        isOutlier = grubbsTest_max_oneTailed(arr[:len(arr)-numOutliers], confidenceLevel);
        if (isOutlier):
            numOutliers += 1;
    return numOutliers;

def grubbsTest_max_oneTailed(arr, confidenceLevel):
    #implementing https://en.wikipedia.org/wiki/Grubbs%27_test_for_outliers
    #but for one tailed and only checking the max
    G = getG_max_oneTailed(arr);
    N = len(arr)
    threshold = getGrubbsThreshold_oneTailed(N, confidenceLevel);
    print(len(arr),G)
    print(len(arr),threshold)
    return G > threshold;
    
def getG_max_oneTailed(arr):
    arr = util.npArrayIfList(arr);
    assert len(arr.shape)==1\
            , "should be a 1d array but got shape: "+str(arr.shape);
    arrExcludingLastVal = arr[:-1];
    mean = np.mean(arr)
    std = np.sqrt(np.sum(np.square(arr-mean))/float((len(arr)-1)))
    theMax = np.max(arr)
    G = (theMax-mean)/std;
    return G;

def getGrubbsThreshold_oneTailed(N, confidenceLevel):
    tTestValue = stats.t.ppf(1-(confidenceLevel/(N)), N-2)
    threshold = ((N-1)/np.sqrt(N))*np.sqrt((tTestValue**2)/(N-2+(tTestValue**2)))
    return threshold;
    
        
    
    
