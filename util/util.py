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
import datetime;
import smtplib;
import random;
import glob;
import json;
from collections import OrderedDict;

DEFAULT_LETTER_ORDERING = ['A','C','G','T'];
DEFAULT_BACKGROUND_FREQ=OrderedDict([('A',0.3),('C',0.2),('G',0.2),('T',0.3)]);
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
        replace = self.bestObject==None or self.isBetter(val);
        if (replace):
            self.bestObject = theObject;
            self.bestVal = val;  
        return replace;
    def isBetter(self, val):
        raise NotImplementedError();
    def getBest(self):
        return self.bestObject, self.bestVal;
    def getBestVal(self):
        return self.bestVal;
    def getBestObj(self):
        return self.bestObject;

class GetBest_Max(GetBest):
    def isBetter(self, val):
        return val > self.bestVal;

class GetBest_Min(GetBest):
    def isBetter(self, val):
        return val < self.bestVal;

def addDictionary(toUpdate, toAdd, initVal=0, mergeFunc = lambda x, y: x+y):
    """
        Defaults to addition, technically applicable any time you want to 
        update a dictionary (toUpdate) with the entries of another dictionary
        (toAdd) using a particular operation (eg: adding corresponding keys)
    """
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

def enum2(**enums):
    toReturn = type('Enum', (), enums);
    toReturn.vals = enums.values();
    return toReturn;

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

def sampleWithoutReplacement(arr, numToSample):
    arrayCopy = [x for x in arr];
    for i in xrange(numToSample):
        randomIndex = int(random.random()*(len(arrayCopy)-i))+i; 
        swapIndices(arrayCopy, i, randomIndex);
    return arrayCopy[0:numToSample];

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
    fileHandle = open(fileName);
    return parseYamlFileHandle(fileHandle);

def parseYamlFileHandle(fileHandle):
    import yaml;
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

#returns the string of the traceback
def getErrorTraceback():
    import traceback
    return traceback.format_exc()

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

def intersects(chromStartEnd1, chromStartEnd2):
    if (chromStartEnd1[0] != chromStartEnd2[0]):
        return False;
    else:
        #"earlier" is the one with the earlier start coordinate.
        if (chromStartEnd1[1] < chromStartEnd2[1]): 
            earlier = chromStartEnd1;
            later = chromStartEnd2;
        else:
            earlier = chromStartEnd2;
            later = chromStartEnd1;
        #"intersects" if starts before the later one ends, and ends after the later one
        #starts. Note that I am assuming 0-based start and 1-based end, a la string indexing.
        if ((earlier[1] < later[2]) and (earlier[2] > later[1])):
            return True;
        else:
            return False;

def readInChromSizes(chromSizesFile):
    import fileProcessing as fp;
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
        , transformation=fp.defaultTabSeppd
        , action=action 
    )

def linecount(filename):
    import subprocess;
    out = subprocess.Popen(
            ['wc', '-l', filename]
            ,stdout=subprocess.PIPE
            ,stderr=subprocess.STDOUT).communicate()[0]
    out = out.strip();
    print(out);
    return int(out.split(' ')[0])

def defaultTransformation():
    import fileProcessing as fp;
    return chainFunctions(fp.trimNewline, fp.splitByTabs);

class ArgumentToAdd(object):
    """
        Class to append runtime arguments to a string
        to facilitate auto-generation of output file names.
    """
    def __init__(self, val, argumentName=None, argNameAndValSep="-"):
        self.val = val;
        self.argumentName = argumentName;
        self.argNameAndValSep = argNameAndValSep;
    def argNamePrefix(self):
        return ("" if self.argumentName is None else self.argumentName+str(self.argNameAndValSep))
    def transform(self):
        return self.argNamePrefix()+str(self.val);

class BooleanArgument(ArgumentToAdd):
    def transform(self):
        assert self.val; #should be True if you're calling transformation
        return self.argumentName;

class CoreFileNameArgument(ArgumentToAdd):
    def transform(self):
        import fileProcessing as fp;
        return self.argNamePrefix()+fp.getCoreFileName(self.val);

class ArrArgument(ArgumentToAdd):
    def __init__(self, val, argumentName, sep="+", toStringFunc=str):
        super(ArrArgument, self).__init__(val, argumentName);
        self.sep = sep;
        self.toStringFunc=toStringFunc;
    def transform(self):
        return self.argNamePrefix()+self.sep.join([self.toStringFunc(x) for x in self.val]);

class ArrOfFileNamesArgument(ArrArgument):
    def __init__(self, val, argumentName, sep="+"):
        import fileProcessing as fp;
        super(ArrOfFileNamesArgument, self).__init__(val, argumentName, sep, toStringFunc=lambda x: fp.getCoreFileName(x));

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

class TitledMappingIterator(object):
    """
        Returns an iterator over TitledArrs for the keys in titledMapping.mapping
    """
    def __init__(self, titledMapping):
        self.titledMapping = titledMapping;
        self.keysIterator = iter(titledMapping.mapping);
    def next(self):
        nextKey = self.keysIterator.next();
        return self.titledMapping.getTitledArrForKey(nextKey);

class TitledMapping(object):
    """
        When each key maps to an array, and each index in the array is associated with
            a name.
    """
    def __init__(self, titleArr, flagIfInconsistent=False):
        self.mapping = OrderedDict(); #mapping from name of a key to the values
        self.titleArr = titleArr;
        self.colNameToIndex = dict((x,i) for (i,x) in enumerate(self.titleArr));
        self.rowSize = len(self.titleArr);
        self.flagIfInconsistent = flagIfInconsistent;
    def keyPresenceCheck(self, key):
        """
            Throws an error if the key is absent
        """
        if (key not in self.mapping):
            raise RuntimeError("Key "+str(key)+" not in mapping; supported feature names are "+str(self.mapping.keys()));
    def getArrForKey(self, key):
        self.keyPresenceCheck(key);
        return self.mapping[key]
    def getTitledArrForKey(self, key):
        """
            returns an instance of util.TitledArr which has: getCol(colName) and setCol(colName)
        """
        return TitledArr(self.titleArr, self.getArrForKey(key), self.colNameToIndex); 
    def addKey(self, key, arr):
        if (len(arr) != self.rowSize):
            raise RuntimeError("arr should be of size "+str(self.rowSize)+" but is of size "+str(len(self.arr)));
        if (self.flagIfInconsistent):
            if key in self.mapping:
                if (str(self.mapping[key]) != str(arr)):
                    raise RuntimeError("Tired to add "+str(arr)+" for key "+str(key)+" but "+str(self.mapping[key])+" already present");
        self.mapping[key] = arr;
    def __iter__(self):
        """
            Iterator is over instances of TitledArr!
        """
        return TitledMappingIterator(self);
    def printToFile(self, fileHandle, includeRownames=True):
        import fileProcessing as fp;
        fp.writeMatrixToFile(fileHandle, self.mapping.values(), self.titleArr, [x for x in self.mapping.keys()]);

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
            if (len(arr) != len(self.colNames)):
                raise RuntimeError("There are "+str(len(self.colNames))+" column names but only "+str(len(arr))+" columns in this row");
    def normaliseRows(self):
        self.rows = rowNormalise(np.array(self.rows));
    def printToFile(self, fileHandle):
        import fileProcessing as fp;
        fp.writeMatrixToFile(fileHandle, self.rows, self.colNames, self.rowNames);

class TitledArr(object):
    def __init__(self, title, arr, colNameToIndex=None):
        assert len(title)==len(arr);
        self.title = title;
        self.arr = arr;
        self.colNameToIndex = colNameToIndex;
    def getCol(self, colName):
        assert self.colNameToIndex is not None;
        return self.arr[self.colNameToIndex[colName]]
    def setCol(self, colName, value):
        assert self.colNameToIndex is not None;
        self.arr[self.colNameToIndex[colName]] = value;

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

def objectFromArgsAndKwargs(classOfObject, args=[], kwargs={}):
    return classOfObject(args, kwargs);
def objectFromArgsAndKwargsFromYaml(classOfObject, yamlWithArgsAndKwargs):
    return objectFromArgsAndKwargs(classOfObject, yamlWithArgsAndKwargs['args'] if 'args' in yamlWithArgsAndKwargs else [], yamlWithArgsAndKwargs['kwargs'] if 'kwargs' in yamlWithArgsAndKwargs else '');

def arrayEquals(arr1, arr2):
    """
        compares corresponding entries in arr1 and arr2
    """
    return all((x==y) for (x,y) in zip(arr1, arr2));

def autovivisect(theDict, getThingToInitialiseWith, *keys):
    for key in keys:
        if key not in theDict:
            theDict[key] = getThingToInitialiseWith();
        theDict = theDict[key];

def setOfSeqsTo2Dimages(sequences):
    import numpy as np;
    toReturn = np.zeros((len(sequences),1,4,len(sequences[0]))); #additional index for channel
    for (seqIdx, sequence) in enumerate(sequences):
        seqTo2DImages_fillInArray(toReturn[seqIdx][0], sequence);
    return toReturn;

def seqTo2Dimage(sequence):
    import numpy as np;
    toReturn = np.zeros((1,4,len(sequence)));
    seqTo2DImages_fillInArray(toReturn[0], sequence);
    return toReturn;

def seqTo2DImages_fillInArray(zerosArray,sequence):
    #zerosArray should be an array of dim 4xlen(sequence), filled with zeros.
    #will mutate zerosArray
    for (i,char) in enumerate(sequence):
        if (char=="A" or char=="a"):
            charIdx = 0;
        elif (char=="C" or char=="c"):
            charIdx = 1;
        elif (char=="G" or char=="g"):
            charIdx = 2;
        elif (char=="T" or char=="t"):
            charIdx = 3;
        elif (char=="N" or char=="n"):
            continue; #leave that pos as all 0's
        else:
            raise RuntimeError("Unsupported character: "+str(char));
        zerosArray[charIdx,i]=1;

def doPCAonFile(theFile):
    import sklearn.decomposition;
    data = np.array(fp.read2DMatrix(fp.getFileHandle(theFile),colNamesPresent=True,rowNamesPresent=True,contentStartIndex=1).rows)
    pca = sklearn.decomposition.PCA();
    pca.fit(data)    
    return pca

def auPRC(trueY, predictedYscores, plotFileName=None):
    from sklearn.metrics import average_precision_score
    from sklearn.metrics import precision_recall_curve
    toReturn = average_precision_score(trueY, predictedYscores);
    if (plotFileName is not None):
        precision, recall, thresholds = precision_recall_curve(trueY, predictedYscores);
        plotPRC(precision, recall, toReturn, plotFileName)
    return toReturn;

def plotPRC(precision, recall, auc, plotFileName):
    import matplotlib.pyplot as plt
    plt.clf()
    plt.plot(recall, precision, label='Precision-Recall curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall: AUC={0:0.2f}'.format(auc))
    plt.legend(loc="lower left")
    plt.savefig(plotFileName)

def assertAttributesHaveTheSameLengths(attributes, attributeNames):
    lens = [len(attribute) for attribute in attributes]
    if (not all([x == lens[0] for x in lens])):
        raise ValueError("all of the following attributes should have the same length: "+", ".join(attributeNames)+"."
                            "Instead, they have lengths: "+", ".join(str(x) for x in lens)); 
    
def splitIgnoringQuotes(string, charToSplitOn=" "):
    """
        will split on charToSplitOn, ignoring things that are in quotes
    """
    string = string.lstrip(); #strip padding whitespace on left
    toReturn = []
    thisWord = []; 
    lastSplitPos = 0;
    inQuote=False;
    for char in string:
        if (inQuote):
            if char=='"':
                inQuote=False;
            else:
                thisWord.append(char); 
        else:
            if char=='"':
                inQuote=True;
            else:
                if char==charToSplitOn:
                    toReturn.append("".join(thisWord));
                    thisWord=[];
                else:
                    thisWord.append(char);
    if len(thisWord) > 0:
        toReturn.append("".join(thisWord));
    print("Parsed arguments:",toReturn); 
    return toReturn;

#for those rare cases where
#you want to have some keyword
#like UNDEF
def getSingleton(name):
    class __Singleton(object):
        def __init__(self):
            pass;
        def __str__(self):
            return name;
    return __Singleton();

def throwErrorIfUnequalSets(given, expected):
    import sets;
    givenSet = sets.Set(given);
    expectedSet = sets.Set(expected);
    inGivenButNotExpected = givenSet.difference(expectedSet);
    inExpectedButNotGiven = expectedSet.difference(givenSet); 
    if (len(inGivenButNotExpected) > 0):
        raise RuntimeError("The following were given but not expected: "+str(inGivenButNotExpected));
    if (len(inExpectedButNotGiven) > 0):
        raise RuntimeError("The following were expected but not given: "+str(inExpectedButNotGiven)); 

def formattedJsonDump(jsonData):
    return json.dumps(jsonData, indent=4
                , separators=(',', ': '))

#TODO: add unit test
def roundToNearest(val, nearest):
    return round(float(val)/float(nearest))*nearest

def sampleFromRangeWithStride(minVal, maxVal, step):
    assert maxVal > minVal;
    toReturn = roundToNearest((random.random()*(maxVal-minVal))+minVal, step);
    assert toReturn >= minVal;
    return toReturn;

def redirectStdoutToString(func, logger=None, emailErrorFunc=None):
    from StringIO import StringIO
    #takes a function, and returns a wrapper which redirects
    #stdout to something else for that function
    #(the function must execute in a thread)
    def wrapperFunc(*args, **kwargs):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = redirectedStdout = StringIO()
        sys.stderr = sys.stdout
        try:
            func(*args, **kwargs);
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            traceback = getErrorTraceback();
            print(traceback);
            if (logger is not None):
                logger.log(traceback);
            if (emailErrorFunc is not None):
                emailErrorFunc(traceback);
            raise e; 
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            stdoutContents = redirectedStdout.getvalue();
            return stdoutContents;
    return wrapperFunc;

def doesNotWorkForMultithreading_redirectStdout(func, redirectedStdout):
    from StringIO import StringIO
    #takes a function, and returns a wrapper which redirects
    #stdout to something else for that function
    #(the function must execute in a thread)
    def wrapperFunc(*args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = redirectedStdout
        func(*args, **kwargs);
        sys.stdout = old_stdout

def dict2str(theDict, sep="\n"):
    return sep.join([key+": "+str(theDict[key]) for key in theDict]);
