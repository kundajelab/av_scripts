#!/usr/bin/python
import sys;
import gzip;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
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
