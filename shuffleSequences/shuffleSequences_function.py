import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
import sys;
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;

def shuffleSequencesInFile_autogenOutputName(sequencesFile,outputFileName=None, progressUpdates=None):
	shuffleSequencesInFile(sequencesFile
		, outputFileName if (outputFileName is not None) else fp.getFileNameParts(sequencesFile).getFilePathWithTransformation(lambda x : "shuffled_"+x)
		, progressUpdates);

def shuffleSequencesInFile(sequencesFile,outputFile,progressUpdates=None):
	fp.transformFile(fp.getFileHandle(sequencesFile),util.chainFunctions(fp.trimNewline,shuffleSequence,fp.appendNewline),outputFile,progressUpdates=progressUpdates);

def shuffleSequence(sequence):
	return ''.join(util.shuffleArray([i for i in sequence]));
