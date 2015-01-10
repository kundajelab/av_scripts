#!/usr/bin/python
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
import sys;
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;
import transformSequencesIntoNeuralNetworkInput_function as tsinnif; 

def getRegionOfLengthFromCenterOf(start, end, length):
    range = getRange(end-start, length);
    return (start + range[0], start + range[1]);

def getRange(lengthOfInput, lengthOfOutput):
    halfLength = int(lengthOfOutput/2);
    remainingLength = lengthOfOutput-halfLength;
    midpoint = int(lengthOfInput/2);
    return (midpoint-halfLength, midpoint+remainingLength); 

def outputFileFromInputFile(options):
	return fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(transformation=lambda x: 'sequencesCentered-'+str(options.sequencesLength)+'_'+x);

def outputTitle(options,sep="\t"):
	toReturn="id";
	toReturn+=sep+"cluster";
	toReturn+=sep+"sequence";
	toReturn += "\n";
	return toReturn;

def recenterSequences(options):
	options.outputFile = options.outputFile if (options.outputFile is not None) else outputFileFromInputFile(options);
	
	def transformation(content):
		toReturn = content[options.columnIdIndex];
		toReturn += "\t"+content[options.clusterColumnIndex];
		toReturn += "\t"+tsinnif.centerSequence(
				content[options.sequencesColumnIndex]
				,options.sequencesLength);	
		toReturn += "\n";
		return toReturn;

	fp.transformFile(
		fp.getFileHandle(options.inputFile)
		,options.outputFile
		,preprocessing=util.chainFunctions(
			fp.trimNewline
			,fp.splitByTabs
		) 
		,filterFunction=filterFunction
		,transformation=transformation
		,progressUpdates=options.progressUpdates
		,outputTitleFromInputTitle = lambda x: outputTitle(options)
		,ignoreInputTitle=True
	)

if __name__ == "__main__":
	parser = argparse.ArgumentParser();
	parser.add_argument('inputFile');
	parser.add_argument('--outputFile', help="if not supplied, output will be named as input file with 'sequencesCentered-size_' prefixed");
	parser.add_argument('--progressUpdates', type=int, default=10000);
	parser.add_argument('--sequencesLength', default=150, help="Region of this size centered on the center will be extracted");
	parser.add_argument('--auxillaryColumnsBefore', default=[0]);
    parser.add_argument('--auxillaryColumnsAfter', default=[]);
	parser.add_argument('--startColIndex',default=1);
	parser.add_argument('--endColIndex', default=2);
	args = parser.parse_args();	
	recenterSequences(args);
