#!/usr/bin/env python
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
import sys;
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;

def shuffleSequencesInFile_autogenOutputName(sequencesFile,outputFileName=None, progressUpdate=None):
	shuffleSequencesInFile(sequencesFile
		, outputFileName if (outputFileName is not None) else fp.getFileNameParts(sequencesFile).getFilePathWithTransformation(lambda x : "shuffled_"+x)
		, progressUpdate);

def shuffleSequencesInFile(sequencesFile,outputFile,progressUpdate=None):
	fp.transformFile(fp.getFileHandle(sequencesFile),outputFile,transformation=util.chainFunctions(fp.trimNewline,shuffleSequence,fp.appendNewline),progressUpdate=progressUpdate);

def shuffleSequence(sequence):
	return ''.join(util.shuffleArray([i for i in sequence]));

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Shuffle sequences in an input file. One line per sequence and nothing more. Note I wrote a different version of this in the enhancer_prediction_code folder for more specific input file format.");
	parser.add_argument('inputFile', help='one line per sequence');
	parser.add_argument('--outputFile', help="if not supplied, output will be named as input file with 'shuffled' prefix");
	parser.add_argument('--progressUpdate', help="If set, will get a progress message every so many lines", type=int);
	args = parser.parse_args();
	shuffleSequences_function.shuffleSequencesInFile_autogenOutputName(args.inputFile, args.outputFile, args.progressUpdate);
main();

