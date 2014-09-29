import sys;

def getFileHandle(filename):
	if (re.search('.gz$',filename) or re.search('.gzip',filename)):
		return gzip.open(filename)
	else:
		return open(filename) 

def splitLinesIntoOtherFiles(fileHandle, preprocessingStep, filterVariableFromLine, outputFileNameFromFilterVariable):
	#read each line from fileHandle
		#apply preprocessing step
		#extract filter variable
		#check hashmap. If not present:
			#generate output file name using filter variable
			#open filehandle. Store in hashmap. 
		#retrieve fileHandle from hashmap.
		#write line to file handle.
	#loop over each fileHandle
		#close it.



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

class FileNameParts:
	def __init__(self, directory, fileName):
		#also make variables coreFileName and extension
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

def getFileNameParts(fileName):
	#fill out; return an instan
	sys.exit(1);


