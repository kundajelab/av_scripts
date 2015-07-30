from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import pyximport; pyximport.install()
import sys;
import os;
import glob;
import random;
import json;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import datetime;
import smtplib;
import subprocess;
import fileProcessing as fp;
import random;
from collections import OrderedDict;

DEFAULT_LETTER_ORDERING = ['A','C','G','T'];
DEFAULT_BACKGROUND_FREQ=OrderedDict([('A',0.3),('C',0.2),('G',0.2),('T',0.3),('N',0.001)]);
class DiscreteDistribution(object):
    def __init__(self, valToFreq):
        """
            valToFreq: OrderedDict where the keys are the possible things to sample, and the values are their frequencies
        """
        self.valToFreq = valToFreq;
        self.freqArr = valToFreq.values(); #array representing only the probabilities
        self.indexToVal = dict((x[0],x[1]) for x in enumerate(valToFreq.keys())); #map from index in freqArr to the corresponding value it represents
DEFAULT_BASE_DISCRETE_DISTRIBUTION = DiscreteDistribution(DEFAULT_BACKGROUND_FREQ);

class GetBest(object):
    def __init__(self):
        self.bestObject = None;
        self.bestVal = None;
    def process(self, theObject, val):
        if (self.bestObject == None or self.isBetter(val)):
            self.bestObject = theObject;
            self.bestVal = val;  
    def isBetter(self, val):
        raise NotImplementedError();
    def getBest(self):
        return self.bestObject, self.bestVal;

class GetBest_Max(GetBest):
    def isBetter(self, val):
        return val > self.bestVal;

class GetBest_Min(GetBest):
    def isBetter(self, val):
        return val < self.bestVal;

def addDictionary(toUpdate, toAdd, initVal=0, mergeFunc = lambda x, y: x+y):
    for key in toAdd:
        if key not in toUpdate:
            toUpdate[key] = initVal;
        toUpdate[key] = mergeFunc(toUpdate[key], toAdd[key]);

def getExtremeN(toSort, N, keyFunc):
    """
        Returns the indices
    """
    enumeratedToSort = [x for x in enumerate(toSort)];
    sortedVals = sorted(enumeratedToSort, key=lambda x: keyFunc(x[1]));
    return [x[0] for x in sortedVals[0:N]];

class TeeStdOut(object):
    def __init__(self, name, mode='w'):
        dir = os.path.dirname(name)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.file = open(name, mode);
        self.stdout = sys.stdout;
        sys.stdout = self;
    def close(self):
        if self.stdout is not None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.file is not None:
            self.file.close()
            self.file = None
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
    def flush(self):
        self.file.flush()
        self.stdout.flush()
    def __del__(self):
        self.close()

class TeeStdErr(object):
    def __init__(self, name, mode='w'):
        self.file = open(name, mode);
        self.stderr = sys.stderr;
        sys.stderr = self;
    def close(self):
        if self.stderr is not None:
            sys.stderr = self.stderr
            self.stderr = None
        if self.file is not None:
            self.file.close()
            self.file = None
    def write(self, data):
        self.file.write(data)
        self.stderr.write(data)
    def flush(self):
        self.file.flush()
        self.stderr.flush()
    def __del__(self):
        self.close()

reverseComplementLookup = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'
                        , 'a': 't', 't': 'a', 'g': 'c', 'c': 'g','N':'N','n':'n'};
def reverseComplement(sequence):
    reversedSequence = sequence[::-1];
    reverseComplemented = "".join([reverseComplementLookup[x] for x in reversedSequence]);
    return reverseComplemented;

def executeAsSystemCall(commandToExecute):
    print("Executing: "+commandToExecute);
    if (os.system(commandToExecute)):
        raise Exception("Error encountered with command "+commandToExecute);

def executeForAllFilesInDirectory(directory, function, fileFilterFunction = lambda x: True):
    filesInDirectory = glob.glob(directory+"/*");
    filesInDirectory = [aFile for aFile in filesInDirectory if fileFilterFunction(aFile)];
    for aFile in filesInDirectory:
        function(aFile);

def enum(**enums):
    toReturn = type('Enum', (), enums);
    toReturn.vals = enums.values();
    return toReturn;

def getTempDir():
    tempOutputDir = os.environ.get('TMP');
    if (tempOutputDir is None or tempOutputDir == ""):
        raise SystemError("Please set the TMP environment variable to the temp output directory!");
    return tempOutputDir;

#randomly shuffles the input arrays (correspondingly)
#mutates arrs!
def shuffleArray(*arrs):
    if len(arrs) == 0:
        raise ValueError("should supply at least one input array");
    lenOfArrs = len(arrs[0]);
    #sanity check that all lengths are equal
    for arr in arrs:
        if (len(arr) != lenOfArrs):
            raise ValueError("First supplied array had length "+str(lenOfArrs)+" but a subsequent array had length "+str(len(arr)));
    for i in xrange(0,lenOfArrs):
        #randomly select index:
        chosenIndex = random.randint(i,lenOfArrs-1);
        for arr in arrs:
            valAtIndex = arr[chosenIndex];
            #swap
            arr[chosenIndex] = arr[i];
            arr[i] = valAtIndex;
    return arrs;

def chainFunctions(*functions):
    if (len(functions) < 2):
        raise ValueError("input to chainFunctions should have at least two arguments")
    def chainedFunctions(x):
        x = functions[0](x);
        for function in functions[1:]:
            x = function(x);
        return x;
    return chainedFunctions;

def parseJsonFile(fileName):
    fileHandle = open(fileName);
    data = json.load(fileHandle);
    fileHandle.close();
    return data;

def parseYamlFile(fileName):
    import yaml;
    fileHandle = open(fileName);
    data = yaml.load(fileHandle);
    fileHandle.close();
    return data;

def parseMultipleYamlFiles(pathsToYaml):
    parsedYaml = {};
    for pathToYaml in pathsToYaml:
        parsedYaml.update(parseYamlFile(pathToYaml));
    return parsedYaml; 

def checkForAttributes(item, attributesToCheckFor, itemName=None):
    for attributeToCheckFor in attributesToCheckFor:
        if hasattr(item,attributeToCheckFor)==False:
            raise Exception("supplied item "+("" if itemName is None else itemName)+" should have attribute "+attributeToCheckFor);

def transformType(inp,theType):
    if (theType == "int"):
        return int(inp);
    elif (theType == "float"):
        return float(inp);
    elif (theType == "str"):
        return str(inp);
    else:
        raise ValueException("Unrecognised type "+theType);

class Entity(object):
    def __init__(self,id):
        self.id = id;
        self.attributes = {'id': id};
    def addAttribute(self,attributeName, value):
        if (attributeName in self.attributes):
            if (self.attributes[attributeName] != value):
                raise ValueError("Attribute "+attributeName+" already exists for "+str(self.id)+" and has value "+str(self.attributes[attributeName])+" which is not "+str(value)+"\n");
        self.attributes[attributeName] = value;
    def getAttribute(self,attributeName):
        if (attributeName in self.attributes):
            return self.attributes[attributeName];
        else:
            raise ValueError("Attribute "+attributeName+" not present on entity "+self.id+". Present attributes are: "+str(self.attributes.keys()));
    def hasAttribute(self,attributeName):
        return attributeName in self.attributes;

def printAttributes(entities,attributesToPrint,outputFile):
    title = "id";
    for attribute in attributesToPrint:
        title += "\t"+attribute;
    f = open(outputFile, 'w');
    f.write(title+"\n");
    for entity in entities:
        line = entity.id;
        for attribute in attributesToPrint:
            line += "\t"+str(entity.getAttribute(attribute));
        f.write(line+"\n");
    f.close();

def floatRange(start,end,step):
    """ Like xrange but for floats..."""
    val = start;
    while (val <= end):
        yield val;
        val += step;
    
class VariableWrapper():
    """ For when I want reference-type access to an immutable"""
    def __init__(self, var):
        self.var = var;   

def getMaxIndex(arr):
    maxSoFar = arr[0];
    maxIndex = 0;
    for i in xrange(0,len(arr)):
        if maxSoFar < arr[i]:
            maxSoFar = arr[i];
            maxIndex = i;
    return maxIndex;

def splitIntegerIntoProportions(integer,proportions):
    #just assign 'floor' proportion*integer to each one, and give the leftovers to the largest one.
    sizesToReturn = [int(integer*prop) for prop in proportions];
    total = sum(sizesToReturn);
    leftover = integer - total;
    sizesToReturn[getMaxIndex(proportions)] += leftover;
    return sizesToReturn;

def getDateTimeString(datetimeFormat="%y-%m-%d-%H-%M"):
    today = datetime.datetime.now();
    return datetime.datetime.strftime(today,datetimeFormat) 


def sendEmail(to,frm,subject,contents):
    from email.mime.text import MIMEText;
    msg = MIMEText(contents);
    msg['Subject'] = subject;
    msg['From'] = frm;
    msg['To'] = str(to);
    s = smtplib.SMTP('smtp.stanford.edu')
    s.starttls();
    s.sendmail(frm, to, msg.as_string())
    s.quit()

def assertMutuallyExclusiveAttributes(obj, attrs):
    arr = [presentAndNotNone(obj,attr) for attr in attrs];
    if (sum(arr) > 1):
        raise AssertionError("At most one of "+str(attrs)+" should be set");

def presentAndNotNone(obj,attr):
    if (hasattr(obj,attr) and getattr(obj,attr) is not None):
        return True;
    else:
        return False;

def presentAndNotNoneOrFalse(obj,attr):
    if (hasattr(obj,attr) and getattr(obj,attr) is not None and getattr(obj,attr) != False):
        return True;
    else:
        return False;

def absentOrNone(obj,attr):
    return (presentAndNotNone(obj,attr)==False);

def assertHasAttributes(obj,attributes, explanation):
    for attr in attributes:
        if (absentOrNone(obj,attr)):
            raise AssertionError(attr,"should be set;",explanation);

def assertDoesNotHaveAttributes(obj,attributes,explanation):
    for attr in attributes:
        if (presentAndNotNone(obj,attr)):
            raise AssertionError(attr,"should not be set;",explanation);

def sumNumpyArrays(numpyArrays):
    import numpy as np;
    arr = np.zeros(numpyArrays[0].shape);
    for i in xrange(0,len(numpyArrays)):
        arr += numpyArrays[i];
    return arr;

def avgNumpyArrays(numpyArrays):
    theSum = sumNumpyArrays(numpyArrays);
    return theSum / float(len(numpyArrays));

def invertIndices(selectedIndices, fullSetOfIndices):
    """
        Returns all indices in fullSet but not in selected.
    """
    selectedIndicesDict = dict((x, True) for x in selectedIndices);
    return [x for x in fullSetOfIndices if x not in selectedIndicesDict];

def invertPermutation(permutation):
    inverse = [None]*len(permutation);
    for newIdx, origIdx in enumerate(permutation):
        inverse[origIdx] = newIdx;
    return inverse;

def valToIndexMap(arr):
    """
        A map from a value to the index at which it occurs
    """
    return dict((x[1],x[0]) for x in enumerate(arr)); 

def arrToDict(arr):
    """
        Turn an array into a dictionary where each value maps to '1';
        used for membership testing.
    """
    return dict((x,1) for x in arr);

def splitChromStartEnd(chromId):
    chrom_startEnd = chromId.split(":");
    chrom = chrom_startEnd[0];
    start_end = chrom_startEnd[1].split("-");
    return (chrom, int(start_end[0]), int(start_end[1]));

def makeChromStartEnd(chrom, start, end):
    return chrom+":"+str(start)+"-"+str(end); 

def readInChromSizes(chromSizesFile):
    chromSizes = {};
    def action(inp, lineNumber):
        if (lineNumber == 0):
            assert inp[0] == "chrom"; #sanity check that first column called 'chrom'
        else:
            chrom = inp[0];
            size = int(inp[1]);
            assert chrom not in chromSizes;
            chromSizes[chrom] = size;
    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(chromSizesFile)
        , transformation=util.chainFunctions(fp.trimNewline, fp.splitByTabs)
        , action=action 
    )

def linecount(filename):
    out = subprocess.Popen(
            ['wc', '-l', filename]
            ,stdout=subprocess.PIPE
            ,stderr=subprocess.STDOUT).communicate()[0]
    out = out.strip();
    print(out);
    return int(out.split(' ')[0])

def defaultTransformation():
    return chainFunctions(fp.trimNewline, fp.splitByTabs);

class ArgumentToAdd(object):
    """
        Class to append runtime arguments to a string
        to facilitate auto-generation of output file names.
    """
    def __init__(self, val, argumentName, argNameAndValSep="-"):
        self.val = val;
        self.argumentName = argumentName;
        self.argNameAndValSep = argNameAndValSep;
    def argNamePrefix(self):
        return ("" if self.argumentName is None else self.argumentName)+str(self.argNameAndValSep)
    def transform(self):
        return self.argNamePrefix()+str(self.val);
class BooleanArgument(ArgumentToAdd):
    def transform(self):
        assert self.val; #should be True if you're calling transformation
        return self.argumentName;
class CoreFileNameArgument(ArgumentToAdd):
    def transform(self):
        return fp.getCoreFileName(self.val);
class ArrArgument(ArgumentToAdd):
    def __init__(self, val, argumentName, sep="+", toStringFunc=str):
        super(ArrArgument, self).__init__(val, argumentName);
        self.sep = sep;
        self.toStringFunc=toStringFunc;
    def transform(self):
        return self.sep.join([self.toStringFunc(x) for x in self.val]);

def addArguments(string, args, joiner="_"):
    """
        args is an array of ArgumentToAdd.
    """
    for arg in args:
        string = string+("" if arg.val is None or arg.val is False or (hasattr(arg.val,"__len__") and len(arg.val)==0) else joiner+arg.transform());
    return string;

def check_pid(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def submitProcess(command):
    import subprocess;
    return subprocess.Popen(command);

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

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
            normalisedConfusionMatrix_byRow[row][col] = theMatrix[row][col]/sumEachRow[row];
            normalisedConfusionMatrix_byColumn[row][col] = theMatrix[row][col]/sumEachColumn[col];

    return normalisedConfusionMatrix_byRow, normalisedConfusionMatrix_byColumn, sumEachRow, sumEachColumn;

def sampleFromProbsArr(arrWithProbs):
    """
        Will return a sampled index
    """ 
    randNum = random.random();
    cdfSoFar = 0;
    for (idx, prob) in enumerate(arrWithProbs):
        cdfSoFar += prob;
        if (cdfSoFar >= randNum or idx==(len(arrWithProbs)-1)): #need the
            #letterIdx==(len(row)-1) clause because of potential floating point errors
            #that mean arrWithProbs doesn't sum to 1
            return idx;

def sampleFromDiscreteDistribution(discereteDistribution):
    """
        Expecting an instance of DiscreteDistribution
    """
    return discereteDistribution.indexToVal[sampleFromProbsArr(discereteDistribution.freqArr)];

def sampleNinstancesFromDiscreteDistribution(N, discreteDistribution):
    toReturn = [];
    for i in xrange(N):
        toReturn.append(sampleFromDiscreteDistribution(discreteDistribution));
    return toReturn;

def getFromEnum(theEnum,enumName,string): #for yaml serialisation
    if hasattr(theEnum,string):
        return getattr(theEnum,string);
    else:
        validKeys = [x for x in dir(theEnum) if (not x.startswith("__")) and x != 'vals']
        raise RuntimeError("No "+str(string)+"; support keys for enumName are: "+str(validKeys));
   
class Options(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs);

def getAllPossibleSubsets(arr):
    subsets = [[]];
    for item in arr:
        newSubsets = [];
        for subset in subsets:
            newSubsets.append([item]+subset);
        subsets.extend(newSubsets);
    return subsets;

class TitledMapping(object):
    """
        When each key maps to an array, and each index in the array is associated with
            a name.
    """
    def __init__(self, titleArr):
        self.mapping = OrderedDict(); #mapping from name of a key to the values
        self.titleArr = titleArr;
        self.rowSize = len(self.titleArr);
    def keyPresenceCheck(self, key):
        if (key not in self.mapping):
            raise RuntimeError("Key "+str(key)+" not in mapping; supported feature names are "+str(self.mapping.keys()));
    def getArrForKey(self, key):
        self.keyPresenceCheck(key);
        return self.mapping[key]
    def getTitledArrForKey(self, key):
        return TitledArr(self.titleArr, self.getArrForKey(key)); 
    def addKey(self, key, arr):
        if (len(arr) != self.rowSize):
            raise RuntimeError("arr should be of size "+str(self.rowSize)+" but is of size "+str(len(self.arr)));
        self.mapping[key] = arr;

class Titled2DMatrix(object):
    """
        has a 2D matrix, rowNames and colNames arrays
    """
    def __init__(self, colNamesPresent=False, rowNamesPresent=False
                     , rows=None, colNames=None, rowNames=None):
        """
            Two ways to initialise; either specify rowNamesPresent/colNamesPresent and
                add the actual rows with addRow, or specify rows/colNames/rowNames
                in one shot, and colNamesPresent/rowNamesPresent will be set appropriately.
        """
        if colNames is not None or rowNames is not None:
            if (rows is None):
                raise RuntimeError("If colNames or rowNames is specified, rows should be specified");
        
        if colNames is not None:
            colNamesPresent=True;
        if rowNames is not None:
            rowNamesPresent=True;
        
        self.rows = [] if rows is None else rows;
        self.colNamesPresent = colNamesPresent;
        self.rowNamesPresent = rowNamesPresent;
        self.rowNames = rowNames if rowNames is not None else ([] if rowNamesPresent else None);
        self.colNames = colNames if colNames is not None else ([] if colNamesPresent else None);
    def setColNames(self, colNames):
        assert self.colNamesPresent;
        self.colNames = colNames;
        self.colNameToIndex = dict((x,i) for (i,x) in enumerate(self.colNames));
    def addRow(self, arr, rowName=None):
        assert (self.rowNamesPresent) or (rowName is None);
        self.rows.append(arr);
        if (rowName is not None):
            self.rowNames.append(rowName);
        if (self.colNamesPresent):
            assert len(arr)==len(self.colNames);
    def normaliseRows(self):
        self.rows = rowNormalise(np.array(self.rows));
    def printToFile(self, fileHandle):
        print("rows dim",len(self.rows),len(self.rows[0]));
        fp.writeMatrixToFile(fileHandle, self.rows, self.colNames, self.rowNames);

class TitledArr(object):
    def __init__(self, title, arr):
        assert len(title)==len(arr);
        self.title = title;
        self.arr = arr;

def rowNormalise(matrix):
    import numpy as np;
    rowSums = np.sum(matrix,axis=1);
    rowSums = rowSums[:,None]; #expand for axis compatibility
    return matrix/rowSums;

def computeCooccurence(matrix):
    """
        matrix: rows (first dim) are examples
    """
    import numpy;
    coocc = matrix.T.dot(matrix);
    return rowNormalise(coocc);

def swapIndices(arr, idx1, idx2):
    temp = arr[idx1];
    arr[idx1] = arr[idx2];
    arr[idx2] = temp;

def sampleWithoutReplacement(arr, numToSample):
    arrayCopy = [x for x in arr];
    for i in xrange(numToSample):
        randomIndex = int(random.random()*(len(arrayCopy)-i))+i; 
        swapIndices(arrayCopy, i, randomIndex);
    return arrayCopy[0:numToSample];
    

