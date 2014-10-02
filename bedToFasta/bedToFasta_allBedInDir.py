#!/usr/bin/python
import sys;
sys.path.insert(0,"/home/avanti/av_scripts/");
import pathSetter;
import bedToFasta_allBedInDir_function;

#executes bedToFasta on all bed files in a directory
def main():
	if (len(sys.argv) < 2):
		print "arguments: [inputDir] [finalOutputFile]";
		sys.exit(1);

	inputDir = sys.argv[1];
	finalOutputFile = sys.argv[2];
	bedToFasta_allBedInDir_function.bedToFastaForAllBedInDirectory(inputDir, finalOutputFile);

main();
