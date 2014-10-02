#!/usr/bin/python
import bedToFasta;
import util;

#executes bedToFasta on all bed files in a directory
def main():
	if (len(sys.argv) < 2):
		print "arguments: [inputDir] [finalOutputFile]";
		sys.exit(1);

	inputDir = sys.argv[1];
	finalOutputFile = sys.argv[2];

def bedToFastaForAllFilesInDirectory(inputDir, finalOutputFile):
	inputBedFiles = glob.glob(inputDir);
	tempDir = util.getTempDir();
	outputFileFromInputFile = lambda inputFile: tempDir + "/" + "fastaExtracted_" + fp.getFileNameParts(inputBedFile).coreFileName + ".tsv";
	pathToFaFromChrom = lambda chrom : "/home/avanti/Enhancer_Prediction/EncodeHg19MaleMirror/"+chrom+".fa";
	executeForAllFilesInDirectory(inputBedFiles, 
		lambda anInput : bedToFasta(anInput, outputFileFromInputFile(anInput), pathToFaFromChrom));

	#concatenate files using cat
	fp.concatenateFiles(finalOutputFile, [outputFileFromInputFile(inputBedFile) for inputBedFile in inputBedFiles]);

main(); 
