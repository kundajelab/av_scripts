import sys;
import glob;
sys.path.insert(0,"/home/avanti/av_scripts");
import pathSetter;
import bedToFasta_function;
import fileProcessing as fp;
import util;

def bedToFastaForAllBedInDirectory(inputDir, finalOutputFile):
	inputBedFiles = glob.glob(inputDir+"/*");
	tempDir = util.getTempDir();
	outputFileFromInputFile = lambda inputFile: tempDir + "/" + "fastaExtracted_" + fp.getFileNameParts(inputFile).coreFileName + ".tsv";
	pathToFaFromChrom = lambda chrom : "/home/avanti/Enhancer_Prediction/EncodeHg19MaleMirror/"+chrom+".fa";
	util.executeForAllFilesInDirectory(inputDir, 
		lambda anInput : bedToFasta_function.bedToFasta(anInput, outputFileFromInputFile(anInput), pathToFaFromChrom));

	#concatenate files using cat
	fp.concatenateFiles(finalOutputFile, [outputFileFromInputFile(inputBedFile) for inputBedFile in inputBedFiles]);

