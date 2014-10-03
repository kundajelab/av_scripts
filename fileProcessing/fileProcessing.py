import sys;
import re;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import util;
import gzip;

def getFileNameParts(fileName):
	p = re.compile(r"^(.*/)?([^\./]+)(\.[^/]*)?$");
	m = p.search(fileName);
	return FileNameParts(m.group(1), m.group(2), m.group(3));

class FileNameParts:
	def __init__(self, directory, coreFileName, extension):
		self.directory = directory if (directory is not None) else os.getcwd();
		self.coreFileName = coreFileName;
		self.extension = extension;
	def getFullPath(self):
		return self.directory+"/"+self.fileName;
	def getCoreFileNameWithTransformation(self, transformation):
		return transformation(self.coreFileName);
	def getFileNameWithTransformation(self,transformation,extension=None):
		toReturn = self.getCoreFileNameWithTransformation(transformation);
		if (extension is not None):
			toReturn = toReturn+extension;
		else:
			if (self.extension is not None):
				toReturn = toReturn+self.extension;
		return toReturn;
	def getFilePathWithTransformation(self,transformation,extension=None):
		return self.directory+"/"+self.getFileNameWithTransformation(transformation,extension=extension);

def getFileHandle(filename):
	if (re.search('.gz$',filename) or re.search('.gzip',filename)):
		return gzip.open(filename)
	else:
		return open(filename) 

#returns an array of all filter variables.
def splitLinesIntoOtherFiles(fileHandle, preprocessingStep, filterVariableFromLine, outputFilePathFromFilterVariable):
	filterVariablesToReturn = []
	filterVariableToOutputFileHandle = {};
	for line in fileHandle:
		processedLine = line;
		if (preprocessingStep is not None):
			processedLine = preprocessingStep(processedLine);
		filterVariable = filterVariableFromLine(processedLine);
		if (filterVariable not in filterVariableToOutputFileHandle):
			outputFilePath = outputFilePathFromFilterVariable(filterVariable);
			filterVariablesToReturn.append(filterVariable);
			outputFileHandle = open(outputFilePath, 'w');
			filterVariableToOutputFileHandle[filterVariable] = outputFileHandle;
		outputFileHandle = filterVariableToOutputFileHandle[filterVariable];
		outputFileHandle.write(line)
	for fileHandle in filterVariableToOutputFileHandle.items():
		fileHandle[1].close();
	return filterVariablesToReturn;

#transformation has a specified default so that this can be used to, for instance, unzip a gzipped file.
def transformFile(fileHandle, outputFile, transformation=lambda x: x, progressUpdates=None):
	outputFileHandle = open(outputFile, 'w');
	i = 0;
	for line in fileHandle:
		i += 1;
		printProgress(progressUpdates, i);
		outputFileHandle.write(transformation(line));
	outputFileHandle.close();

def transformFileIntoArray(fileHandle, transformation=lambda x: x, progressUpdates=None):
	i = 0;
	toReturn = [];
	for line in fileHandle:
		i += 1;
		printProgress(progressUpdates, i);
		toReturn.append(transformation(line));
	return toReturn;
			
def printProgress(progressUpdates, i):
	if progressUpdates is not None:
		if (i%progressUpdates == 0):
			print "Processed "+str(i)+" lines";

def trimNewline(s):
	return s.rstrip('\r\n');

def appendNewline(s):
	return s+"\n"; #aargh O(n) aargh FIXME if you can

def splitByDelimiter(s,delimiter):
	return s.split(delimiter);

def splitByTabs(s):
	return splitByDelimiter(s,"\t");

def stringToFloat(s):
	return float(s);

def stringToInt(s):
	return int(s);

def lambdaMaker_getAtPosition(index):
	return (lambda x: x[index]);

def lambdaMaker_insertSuffixIntoFileName(suffix,separator):
	return lambda fileName: getFileNameParts(fileName).getFileNameWithTransformation(
			lambda coreFileName: coreFileName+separator+suffix
	);
def lambdaMaker_insertPrefixIntoFileName(prefix, separator):
	return lambda fileName: getFileNameParts(fileName).getFileNameWithTransformation(
		lambda coreFileName: prefix+separator+coreFileName
	);

#wrapper for the cat command
def concatenateFiles(outputFile, arrOfFilesToConcatenate):
	util.executeAsSystemCall("cat "+(" ".join(arrOfFilesToConcatenate))+" > "+outputFile);

