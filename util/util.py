from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
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
        if key in toUpdate:
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
                        , 'a': 't', 't': 'a', 'g': 'c', 'c': 'g','N':'N'};
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
        return "" if self.argumentName is None else self.argumentName+self.argNameAndValSep
    def transform(self):
        return self.argNamePrefix()+str(self.val);
class BooleanArgument(ArgumentToAdd):
    def transformation(self):
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
        string = string+("" if arg.val is None or arg.val is False else joiner+arg.transform());
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
 
