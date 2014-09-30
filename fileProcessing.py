import sys;
import re;
import os;

def getFileNameParts(fileName):
	p = re.compile(r"^(.*/)?([^\./])+(\\..*)?$");
	m = p.match(fileName);
	return FileNameParts(m.group(1), m.group(2), m.group(3));

class FileNameParts:
	def __init__(self, directory, coreFileName, extension):
		self.directory = directory if (directory != "") else os.getcwd();
		self.coreFileName = coreFileName;
		self.extension = extension;
	def getFileName(self):
		return self.fileName;
	def getDirectory(self):
		return self.directory;
	def getFullPath(self):
		return self.directory+"/"+self.fileName;
	def getCoreFileName(self):
		return coreFileName;
	def getCoreFileNameWithTransformation(self, transformation):
		return transformatio(coreFileName);
	def getFileNameWithTransformation(self,transformation):
		toReturn = self.getCoreFileNameWithTransformation(transformation);
		if (extension is not None):
			toReturn = toReturn+"."+extension;
		return toReturn;
	def getFilePathWithTransformation(self,transformation):
		return self.directory+"/"+self.getFileNameWithSuffixInserted(transformation);

def getFileHandle(filename):
	if (re.search('.gz$',filename) or re.search('.gzip',filename)):
		return gzip.open(filename)
	else:
		return open(filename) 

#returns an array of all the files produced.
def splitLinesIntoOtherFiles(fileHandle, preprocessingStep, filterVariableFromLine, outputFilePathFromFilterVariable):
	filePathsToReturn = [];
	filterVariableToOutputFileHandle = {};
	for line in fileHandle:
		processedLine = line;
		if (preprocessingStep is not None):
			processedLine = preprocessingStep(processedLine);
		filterVariable = filterVariableFromLine(processedLine);
		if (filterVariable not in filterVariableToOutputFileHandle):
			outputFilePath = outputFilePathFromFilterVariable(filterVariable);
			filePathsToReturn.append(outputFilePath);
			f = open(outputFilePath, 'w');
			filterVariableToOutputFileHandle[filterVariable] = outputFileHandle;
		outputFileHandle = filterVariableToOutputFileHandle[filterVariable];
		f.write(line)
	for fileHandle in filterVariableToOutputFileHandle.items():
		fileHandle.close();
	return filePathsToReturn;

def trimNewline(s):
	return s.rstrip('\r\n');

def splitByDelimiter(s,delimiter):
	s = trimNewline(s);
	return s.split(delimiter);

def splitByTabs(s):
	return splitByDelimiter(s,"\t");

def lambdaMaker_getAtPosition(index):
	return (lambda x: x[index]);

def lambdaMaker_insertSuffix(suffix,separator):
	return lambda coreFileName: coreFileName+separator+suffix;
def lambdaMaker_inserPrefix(prefix):
	return lambda coreFileName: prefix+separator+coreFileName;
def lambdaMaker_insertPrefixWithUnderscore(prefix):
	return insertPrefix(prefix,"_");
def lambdaMaker_insertSuffixWithUnderscore(suffix):
	return insertSuffix(suffix,"_");



