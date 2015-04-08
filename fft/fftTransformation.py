#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import util;
import fileProcessing as fp;
import numpy as np;

def takeFFT(signal): #will drop the symmetric bit
    numFreqsToConsider = int(len(signal)/2) +  len(signal)%2;
    theFFT = np.fft.fft(signal);
    return theFFT[0:numFreqsToConsider];
 
def getFFTaction(actionOnFFT, titlePresent, actionOnTitle=None):
    def action(inp, lineNumber):
        numFreqsToConsider = int((len(inp)-1)/2) + (1 if len(inp-1)%2 == 1 else 0);
    return action;

def fft(options):
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "fftApplied_"+x);
    outputFileHandle = fp.getFileHandle(outputFile, 'w');
    def action(inp, lineNumber):
        if lineNumber == 1:
            numFreqsToConsider = int((len(inp)-1)/2) +  (len(inp)-1)%2; #ew hacky
            outputFileHandle.write("\t".join([str(x) for x in inp[:numFreqsToConsider]])+"\n"); 
        else:
            theId = inp[0];
            signal = [float(x) for x in inp[1:]];
            theFFT = takeFFT(signal);
            powerSpectrum = abs(theFFT);   
            outputFileHandle.write(theId+"\t"+"\t".join([str(x) for x in powerSpectrum])+"\n")
    fp.performActionOnEachLineOfFile(
        fp.getFileHandle(options.inputFile)
        , transformation=fp.defaultTabSeppd
        , action=action
        , ignoreInputTitle=False
        , progressUpdate = options.progressUpdate
    );
    outputFileHandle.close();

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputFile", required=True);
    parser.add_argument("--progressUpdate", type=int);
    options = parser.parse_args(); 
    fft(options);
