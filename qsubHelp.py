import sys;
sys.path.insert(0, "..");
import fileProcessing as fp;

class QsubHeaderClass:
	def __init__(
		self
		, jobName
		, email=None
		, maxMem=None
		, maxRuntime=None
		, numCores=None
		, workingDir=None #if set to none, uses the cwd option
		, stdoutPath=None #set to false if don't want it. Will default to something based on jobname otherwise
		, stdErrPath=None #''
	):
		self.email = email;
		self.jobName = jobName;
		self.maxMem= maxMem;
		self.maxRuntime = maxRuntime;
		self.numCores = numCores;
		self.workingDir = workingDir;
		self.stdoutPath = stdoutPath;
		self.stdErrPath = stdErrPath;
	
	def setOutputPathsBasedOnFilePath(self,filePath):
		fileNameParts = fp.getFileNameParts(filePath);
		directory = fileNameParts.getDirectory();
		coreFileName = fileNameParts.getCoreFileName();
		self.stdoutPath = directory+"/"+coreFileName+".stdout";
		self.stderrPath = directory+"/"+coreFileName+".stderr";
	
	def produceHeader(self):
		toReturn = "#!/bin/sh\n";
		toReturn += "$ -N "+jobName+"\n";
		if (email is not None):
			toReturn += "$ -m ea\n";
			toReturn += "$ -M "+email+"\n";
		if (maxMem is not None):
			toReturn += "$ -l "+maxMem+"\n";
		if (maxRuntime is not None):
			toReturn += "$ -l h_rt="+maxRuntime+"\n";
		if (numCores is not None):
			toReturn += "$ -pe shm "+numCores+"\n";
		if (workingDir is not None):
			toReturn += "$ -wd "+workingDir+"\n";
		else:
			toReturn += "$ -cwd\n";
		if (stdoutPath is None):
			stdoutPath = jobName+".stdout";
		if (stderrPath is None):
			stderrPath = jobName+".stderr";
		if (stdoutPath != False):
			toReturn += "$ -o "+stdoutPath+"\n";
		if (stderrPath != False):
			toReturn += "$ -e "+stderrPath+"\n";
		return toReturn;

def writeQsubFile(filePath, qsubHeader, command):
	f = open(filePath,'w');
	f.write(qsubHeader.produceHeader());
	f.write(command);
	f.close();






	


