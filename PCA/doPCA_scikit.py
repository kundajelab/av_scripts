#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;

def doPCA(matrixFile, options):
    import sklearn.decomposition;
    import numpy as np;
    the2DMatrix = fp.read2DMatrix(fp.getFileHandle(matrixFile),colNamesPresent=(options.colNamesAbsent==False),rowNamesPresent=(options.rowNamesAbsent==False),contentStartIndex=options.contentStartIndex);
    data = np.array(the2DMatrix.rows)
    pca = sklearn.decomposition.PCA();
    pca.fit(data)
    return pca

def doPCAandWriteToFile(matrixFile, options):
    pca = doPCA(matrixFile, options);
    import pickle;
    outputFileName = fp.getFileNameParts(matrixFile).getFilePathWithTransformation(lambda x: "pca_"+x, extension=".pkl");
    pickle.dump(pca,fp.getFileHandle(outputFileName,'w'));


if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser("Will do pca using scikit and dump the scikit pca object");
    parser.add_argument("--matrixFiles", nargs="+", required=True);
    parser.add_argument("--colNamesAbsent", action="store_true");
    parser.add_argument("--rowNamesAbsent", action="store_true");
    parser.add_argument("--contentStartIndex");
    
    options = parser.parse_args();
    for matrixFile in options.matrixFiles:
        print("Doing",matrixFile);
        doPCAandWriteToFile(matrixFile, options); 
