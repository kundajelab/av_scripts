import sys;
import os;
import glob;
import sys;
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

