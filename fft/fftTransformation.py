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

def getDefaultActionOnTitle(outputFileHandle):
    def action(numFreqsToConsider):
        outputFileHandle.write("\t".join([str(x) for x in inp[:numFreqsToConsider]])+"\n"); 
    return action;
    
def getFFTaction(actionOnFFT, titlePresent, actionOnTitle=None):
    def action(inp, lineNumber):
        numFreqsToConsider = int((len(inp)-1)/2) + (1 if len(inp)%2 == 1 else 0);
        if lineNumber == 1 and titlePresent:
            if (actionOnTitle is not None):
                actionOnTitle(numFreqsToConsider);
        else:
            theId = inp[0];
            signal = [float(x) for x in inp[1:numFreqsToConsider]];   
            actionOnFFT(signal);
    return action;

def fft(options):
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "fftApplied_"+x);
    outputFileHandle = fp.getFileHandle(outputFile, 'w');
    def actionOnFFT(signal):
        powerSpectrum = abs(np.fft.fft(signal));
        outputFileHandle.write(theId+"\t"+"\t".join([str(x) for x in powerSpectrum])+"\n")
    action = getFFTaction(actionOnFFT, titlePresent=True, actionOnTitle=getDefaultActionOnTitle(outputFileHandle)); 
    fp.performActionOnEachLineOfFile(
        fp.getFileHandle(options.inputFile)
        , transformation = fp.defaultTabSeppd
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
