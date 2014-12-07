import sys;
import os;
import glob;
import sys;
import random;
import json;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import datetime;
import smtplib;

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
    print "Executing: "+commandToExecute;
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

def assertHasAttributes(obj,attributes, explanation):
    for attr in attributes:
        if (hasattr(obj,attr) == False or getattr(obj,attr) == None):
            raise AssertionError(attr,"should be set;",explanation);

def assertDoesNotHaveAttributes(obj,attributes,explanation):
    for attr in attributes:
        if (hasattr(obj,attr) and getattr(obj,attr) is not None):
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

 
