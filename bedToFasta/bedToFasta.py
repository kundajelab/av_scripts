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
	if (len(sys.argv) < 4):
		print "arguments: [inputBedFile] [outputFile] [faSequencesDir]";
		sys.exit(1);

	inputBedFile = sys.argv[1];
	finalOutputFile = sys.argv[2];
	sequencesDir = sys.argv[3];
	pathToFaFromChrom = lambda chrom : sequencesDir+"/"+chrom+".fa";

	bedToFasta_function.bedToFasta(inputBedFile, finalOutputFile, faSequencesDir);

main(); 
