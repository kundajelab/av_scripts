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
import numpy as np;
from sklearn.manifold import TSNE;
import util;

def doTSNE(options):
    titled2DMatrix = fp.read2DMatrix(fileHandle = fp.getFileHandle(options.featureFile)
                                    ,colNamesPresent=options.columnNamesAbsent==False
                                    ,rowNamesPresent=options.rowNamesAbsent==False
                                    ,contentEndIndex=options.numColsToConsider);
    model = TSNE(n_components=2, random_state=0);
    result = model.fit_transform(np.array(titled2DMatrix.rows))
    np.save("backupSave.npy", result);
    toSave = util.Titled2DMatrix(rows=result,rowNames=titled2DMatrix.rowNames);
    
    argumentsToAdd = [util.ArgumentToAdd(options.numColsToConsider, "numColsToConsider")];
    prefix = util.addArguments("tsneEmbedding", argumentsToAdd);

    outputFile = fp.getFileNameParts(options.featureFile).getFilePathWithTransformation(lambda x: prefix+"_"+x);
    toSave.printToFile(fp.getFileHandle(outputFile,'w'));

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--featureFile", required=True);
    parser.add_argument("--numColsToConsider", type=int, help="if specified, will consider the first numColsToConsider components");
    parser.add_argument("--columnNamesAbsent", action="store_true");
    parser.add_argument("--rowNamesAbsent", action="store_true");
    options  = parser.parse_args();
    doTSNE(options); 


