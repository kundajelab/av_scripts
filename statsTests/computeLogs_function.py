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
    i = 0;
    while (i < options.upTo):
        if (i > 0):
            (logProduct,product) = updateLogProductAndProduct(i,logProduct,product);
        outputFileHandle.write(str(logProduct)+"\n");
        i += 1;
    outputFileHandle.close();

def computeLogFactorial(num):
    logProduct = 0;
    product = 1;
    i = 0;
    while (i < num):
        if (i > 0):
            (logProduct,product) = updateLogProductAndProduct(i,logProduct,product);
        i += 1;
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
        inputFile = scriptsDir+"/statsTests/logFactorial_30000.txt";
    return [float(x) for x in fp.readRowsIntoArr(fp.getFileHandle(inputFile))];    

LOG_FACTORIAL_ARRAY = readLogFactorialFile();


