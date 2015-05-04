#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
import tables;

DEFAULT_NODE_NAME = "defaultNode";

def init_h5_file(toDiskName, groupName=DEFAULT_NODE_NAME, groupDescription=DEFAULT_NODE_NAME):
    """
        toDiskName: the name of the file on disk
    """
    import tables;
    h5file = tables.openFile(toDiskName, mode="w", title="Dataset")
    gcolumns = h5file.createGroup(h5file.root, groupName, groupDescription)
    return h5file;

class InfoToInitArrayOnH5File(object):
    def __init__(self, name, shape, atomicType):
        """
            name: the name of this matrix
            shape: tuple indicating the shape of the matrix (similar to numpy shapes)
            atomicType: one of the pytables atomic types - eg: tables.Float32Atom() or tables.StringAtom(itemsize=length);

        """
        self.name = name;
        self.shape = shape;
        self.atomicType = atomicType;

def writeToDisk(theH5Column, whatToWrite, batch_size=5000):
    """
        Going to write to disk in batches of batch_size
    """ 
    data_size = len(whatToWrite);
    last = int(data_size / float(batch_size)) * batch_size
    for i in xrange(0, data_size, batch_size):
        stop = (i + data_size%batch_size if i >= last
                else i + batch_size)
        theH5Column.append(whatToWrite[i:stop]);
        h5file.flush()
    
def getH5column(h5file, columnName, nodeName=DEFAULT_NODE_NAME):
    node = h5file.getNode('/', DEFAULT_NODE_NAME);
    return getattr(node, columnName);


def initColumnsOnH5File(h5file, infoToInitArraysOnH5File, expectedRows, nodeName=DEFAULT_NODE_NAME, complib='blosc', complevel=5):
    """
        h5file: filehandle to the h5file, initialised with init_h5_file
        infoToInitArrayOnH5File: array of instances of InfoToInitArrayOnH5File
        expectedRows: this code is set up to work with EArrays, which can be extended after creation.
            (presumably, if your data is too big to fit in memory, you're going to have to use EArrays
            to write it in pieces). "sizeEstimate" is the estimated size of the final array; it
            is used by the compression algorithm and can have a significant impace on performance.
        nodeName: the name of the node being written to.
        complib: the docs seem to recommend blosc for compression...
        complevel: compression level. Not really sure how much of a difference this number makes...
    """
    gcolumns = h5file.getNode(h5file.root, nodeName);
    filters = tables.Filters(complib=complib, complevel=complevel);
    for infoToInitArrayOnH5File in infoToInitArraysOnH5File:
        finalShape = [0]; #in an eArray, the extendable dimension is set to have len 0
        finalShape.extend(infoToInitArrayOnH5File.shape);
        h5file.createEArray(gcolumns, infoToInitArrayOnH5File.name, atom=infoToInitArrayOnH5File.atomicType
                            , shape=finalShape, title=infoToInitArrayOnH5File.name #idk what title does...
                            , filters=filters, expectedrows=expectedRows);
    
def performScikitFit(predictors, outcomes):
    import sklearn.linear_model;
    model = sklearn.linear_model.LinearRegression(predictors, outcomes);
    model.fit(predictors, outcomes);
    print(model.predict([2.0,2.0]));
    
if __name__ == "__main__":
    #Initialise the pytables file
    filename = "demo_h5.pytables";
    h5file = init_h5_file(filename);

    #intiialise the columns going on the file
    predictorsName = "predictors";
    predictorsShape = [2]; #arr describing the dimensions other than the extendable dim.
    outcomesName = "outcomes";
    outcomesShape = []; #the outcome is a vector, so there's only one dimension, the extendable one.
    predictorsInfo = InfoToInitArrayOnH5File(predictorsName, predictorsShape, tables.Float32Atom());
    outcomesInfo = InfoToInitArrayOnH5File(outcomesName, outcomesShape, tables.Float32Atom());
    numSamples = 4;
    
    #write to the file
    initColumnsOnH5File(h5file, [predictorsInfo, outcomesInfo], numSamples);
    predictorsColumn = getH5column(h5file, predictorsName);
    outcomesColumn = getH5column(h5file, outcomesName); 
    writeToDisk(predictorsColumn, [[1.2, 5.4], [2.1, 4.9]]);
    writeToDisk(outcomesColumn, [0.0,0.0]);
    writeToDisk(predictorsColumn, [[5.4,1.2], [4.9,2.1]]);
    writeToDisk(outcomesColumn, [1.0,1.0]);

    #close and reopen
    h5file.close();
    h5file = tables.openFile(filename, mode="r")
    
    #get the predictors and outcomes 
    predictorsColumn = getH5column(h5file, predictorsName);
    outcomesColumn = getH5column(h5file, outcomesName); 
    
    #do anything with them - indexing seems to return
    #something compatible with numpy syntax
    print(predictorsColumn[:]*2)
    print(outcomesColumn[:] + 5)
    #really, stuff just seems to work...
    performScikitFit(predictorsColumn, outcomesColumn);


