#!/usr/bin/python
import sys;
import gzip;
sys.path.insert(0,"/home/avanti/av_scripts/");
import pathSetter;
import bedToFasta_function;

def main():
	if (len(sys.argv) < 3):
		print "arguments: [inputBedFile] [outputFile]";
		sys.exit(1);

	inputBedFile = sys.argv[1];
	finalOutputFile = sys.argv[2];
	pathToFaFromChrom = lambda chrom : "/home/avanti/Enhancer_Prediction/EncodeHg19MaleMirror/"+chrom+".fa";

	bedToFasta_function.bedToFasta(inputBedFile, finalOutputFile, pathToFaFromChrom);

main(); 
