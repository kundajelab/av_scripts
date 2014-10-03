import sys;
sys.path.insert(0, "..");
import fileProcessing as fp;

labBashrcPath = "/srv/gsfs0/projects/kundaje/commonRepository/src/lab_bashrc";

class QsubHeader:
	def __init__(
		self
		, jobName="defaultJobName"
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
	
	def setOutputPathsAndJobNameBasedOnFilePath(self,filePath):
		fileNameParts = fp.getFileNameParts(filePath);
		directory = fileNameParts.directory;
		coreFileName = fileNameParts.coreFileName;
		self.jobName = coreFileName;
		self.stdoutPath = directory+"/"+coreFileName+".stdout";
		self.stderrPath = directory+"/"+coreFileName+".stderr";
	
	def produceHeader(self):
		toReturn = "#!/bin/sh\n";
		toReturn += "#$ -N "+self.jobName+"\n";
		if (self.email is not None):
			toReturn += "#$ -m ea\n";
			toReturn += "#$ -M "+self.email+"\n";
		if (self.maxMem is not None):
			toReturn += "#$ -l h_vmem="+self.maxMem+"\n";
		if (self.maxRuntime is not None):
			toReturn += "#$ -l h_rt="+self.maxRuntime+"\n";
		if (self.numCores is not None):
			toReturn += "#$ -pe shm "+self.numCores+"\n";
		if (self.workingDir is not None):
			toReturn += "#$ -wd "+self.workingDir+"\n";
		else:
			toReturn += "#$ -cwd\n";
		if (self.stdoutPath is None):
			self.stdoutPath = self.jobName+".stdout";
		if (self.stderrPath is None):
			self.stderrPath = self.jobName+".stderr";
		if (self.stdoutPath != False):
			toReturn += "#$ -o "+self.stdoutPath+"\n";
		if (self.stderrPath != False):
			toReturn += "#$ -e "+self.stderrPath+"\n";
		
		toReturn += "source "+labBashrcPath+"\n";

		return toReturn;



def writeQsubFile(filePath, qsubHeader, command):
	f = open(filePath,'w');
	f.write(qsubHeader.produceHeader());
	f.write(command);
	f.close();

def getDefaultHeaderBasedOnFilePath(shellFilePath,theEmail):
	qsubHeader = QsubHeader(email=theEmail);
	qsubHeader.setOutputPathsAndJobNameBasedOnFilePath(shellFilePath);
	return qsubHeader;





	


