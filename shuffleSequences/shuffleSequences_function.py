import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
import sys;
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;

def suffleSequencesInFile_autogenOutputName(sequencesFile,outputFileName=None):
	shuffleSequencesInFile(sequencesFile
		, outputFileName if (outputFileName is not None) else fp.getFileNameParts(sequencesFile).getFilePathWithTransformation(lambda x : "shuffled_"+x));

def shuffleSequencesInFile(sequencesFile,outputFile):
	fp.transformFile(fp.getFileHandle(sequencesFile),util.chainFunctions(fp.trimNewline,shuffleSequence),outputFile);

def shuffleSequence(sequence):
	return ''.join(util.shuffleArray(sequence.split('')));
