
import math;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;


LOG_FACTORIAL_THRESHOLD = 1000; #the threshold at which approximations using logarhythms kick in.
def writeLogFactorialFile(options):
	if (options.outputFile is None):
		options.outputFile = "logFactorial_"+str(options.upTo)+".txt";
	outputFileHandle = open(options.outputFile,"w");
	logProduct = 0;
	product = 1;
	for i in range(0,options.upTo):
		if (i > 0):
			(logProduct,product) = updateLogProductAndProduct(i,logProduct,product);
		outputFileHandle.write(str(logProduct)+"\n");
	outputFileHandle.close();

def computeLogFactorial(num):
	logProduct = 0;
	product = 1;
	for i in range(0,num):
		if (i > 0):
			(logProduct,product) = updateLogProductAndProduct(i,logProduct,product);
	return logProduct;		

def updateLogProductAndProduct(i,logProduct,product):
	if (i > 0):
		if (i <= LOG_FACTORIAL_THRESHOLD):
			product = product*i;
			logProduct = math.log(product);
		else:
			logProduct = math.log(i) + logProduct;
	return (logProduct,product);

def readLogFactorialFile(inputFile=None):
	if (inputFile is None):
		inputFile = os.environ.get("LOG_FACT_FILE");
		if (inputFile is None):
			raise Exception("Please set environment variable LOG_FACT_FILE or supply path to log factorial fil");	
	return fp.transformFileIntoArray(
		fp.getFileHandle(inputFile)
		,transformation=fp.stringToFloat
		,preprocessing=fp.trimNewline
	);	

LOG_FACTORIAL_ARRAY = readLogFactorialFile();


