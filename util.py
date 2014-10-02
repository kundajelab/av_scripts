import os;
import glob;

def executeAsSystemCall(commandToExecute):
	print "Executing: "+commandToExecute;
	if (os.system(commandToExecute)):
		raise "Error encountered with command "+commandToExecute;

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
		print "Please set the TMP environment variable to the temp output directory!";
		raise;
	return tempOutputDir;
