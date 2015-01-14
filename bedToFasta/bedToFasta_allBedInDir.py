#!/usr/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import bedToFasta;
import fileProcessing as fp;
import util;

def bedToFastaForAllBedInDirectory(inputDir, finalOutputFile, faSequencesDir):
	inputBedFiles = glob.glob(inputDir+"/*");
	tempDir = util.getTempDir();
	outputFileFromInputFile = lambda inputFile: tempDir + "/" + "fastaExtracted_" + fp.getFileNameParts(inputFile).coreFileName + ".tsv";
	util.executeForAllFilesInDirectory(inputDir, 
		lambda anInput : bedToFasta_function.bedToFasta(anInput, outputFileFromInputFile(anInput), faSequencesDir));

	#concatenate files using cat
	fp.concatenateFiles_preprocess(
		finalOutputFile
		, [outputFileFromInputFile(inputBedFile) for inputBedFile in inputBedFiles]
		, transformation=lambda line,filename: filename+"\t"+line
		, outputTitleFromInputTitle = lambda x : "sourceBed\tchromosomeLocation\tsequence\n");

#executes bedToFasta on all bed files in a directory
def main():
	if (len(sys.argv) < 3):
		print "arguments: [inputDir] [finalOutputFile] [fastaSequencesDir]";
		sys.exit(1);

	inputDir = sys.argv[1];
	finalOutputFile = sys.argv[2];
	sequencesDir = sys.argv[3];
	bedToFasta_allBedInDir_function.bedToFastaForAllBedInDirectory(inputDir, finalOutputFile, sequencesDir);

main();
