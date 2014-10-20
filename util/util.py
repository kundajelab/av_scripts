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
    return type('Enum', (), enums)

def getTempDir():
	tempOutputDir = os.environ.get('TMP');
	if (tempOutputDir is None or tempOutputDir == ""):
		raise SystemError("Please set the TMP environment variable to the temp output directory!");
	return tempOutputDir;

#randomly shuffles the input array
#mutates arr!
def shuffleArray(arr):
	for i in range(0,len(arr)):
		#randomly select index:
		chosenIndex = random.randint(i,len(arr)-1);
		valAtIndex = arr[chosenIndex];
		#swap
		arr[chosenIndex] = arr[i];
		arr[i] = valAtIndex;
	return arr;

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
                raise ValueError("Attribute "+attributeName+" already exists for "+str(id)+" and has value "+str(self.attributes[attributeName])+" which is not "+str(value)+"\n");
        self.attributes[attributeName] = value;
    def getAttribute(self,attributeName):
        if (attributeName in self.attributes):
            return self.attributes[attributeName];
        else:
            raise ValueError("Attribute "+attributeName+" not present on entity "+self.id);
