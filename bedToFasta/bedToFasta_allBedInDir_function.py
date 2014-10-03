import sys;
import glob;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import bedToFasta_function;
import fileProcessing as fp;
import util;

def bedToFastaForAllBedInDirectory(inputDir, finalOutputFile, faSequencesDir):
	inputBedFiles = glob.glob(inputDir+"/*");
	tempDir = util.getTempDir();
	outputFileFromInputFile = lambda inputFile: tempDir + "/" + "fastaExtracted_" + fp.getFileNameParts(inputFile).coreFileName + ".tsv";
	util.executeForAllFilesInDirectory(inputDir, 
		lambda anInput : bedToFasta_function.bedToFasta(anInput, outputFileFromInputFile(anInput), faSequencesDir));

	#concatenate files using cat
	fp.concatenateFiles(finalOutputFile, [outputFileFromInputFile(inputBedFile) for inputBedFile in inputBedFiles]);

