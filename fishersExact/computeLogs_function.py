
import math;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;

LOG_FACTORIAL_THRESHOLD = 30;

def writeLogFactorialFile(options):
	if (options.outputFile is None):
		options.outputFile = "logFactorial_"+str(options.upTo)+".txt";
	outputFileHandle = open(options.outputFile,"w");
	logProduct = 0;
	product = 1;
	for i in range(0,options.upTo):
		if (i > 0):
			if (i <= flippingPoint):
				product = product*i;
				logProduct = math.log(product);
			else:
				logProduct = math.log(i) + logProduct;
		outputFileHandle.write(str(logProduct)+"\n");
	outputFileHandle.close();

def readLogFactorialFile(inputFile):
	return transformFileIntoArray(
		fp.getFileHandle(inputFile)
		,transformation=fp.stringToFloat
		,preprocessing=fp.trimNewline
	);	



