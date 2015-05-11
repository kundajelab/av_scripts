#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import numpy as np;
import fileProcessing as fp;
import math;
import random;
from collections import OrderedDict;

PWM_FORMAT = util.enum(encodeMotifsFile="encodeMotifsFile");
DEFAULT_LETTER_TO_INDEX={'A':0,'C':1,'G':2,'T':3};

class PWM(object):
    def __init__(self, name, letterToIndex=DEFAULT_LETTER_TO_INDEX):
        self.name = name;
        self.letterToIndex = letterToIndex;
        self.indexToLetter = dict((self.letterToIndex[x],x) for x in self.letterToIndex);
        self._rows = [];
        self._finalsed = False;
    def addRow(self, weights):
        if (len(self._rows) > 0):
            assert len(weights) == len(self._rows[0]);
        self._rows.append(weights);
    def finalise(self, pseudocountProb=0.001):
        assert pseudocountProb >= 0 and pseudocountProb < 1;
        #will smoothen the rows with a pseudocount...
        self._rows = np.array(self._rows);
        self._rows = self._rows*(1-pseudocountProb) + float(pseudocountProb)/len(self._rows[0]);
        for row in self._rows:
            assert(abs(sum(row)-1.0)<0.0001);
        self.logRows = np.log(self._rows);
        self._finalised=True; 
        self.pwmSize = len(self._rows); 
    def getRows(self):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        return self._rows;
    def scoreSeq(self, seq, startIdx, endIdx, background={'A':0.3,'C':0.2,'G':0.2,'T':0.3}):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        assert hasattr(self, 'logRows');
        if ((min(endIdx,len(seq))-max(startIdx,0)) < len(self.logRows)):
            return 0.0; #return 0 when the supplied seq is too short
        score = 0;
        self.logBackground = dict((x,math.log(background[x])) for x in background);
        for idx in xrange(startIdx, endIdx):
            letter = seq[idx];
            if (letter not in self.letterToIndex and (letter=='N' or letter=='n')):
                pass; #just skip the letter
            else:
                score += self.logRows[idx-startIdx, self.letterToIndex[letter]] - self.logBackground[letter];
        return score;
    def sampleFromPwm(self):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        sampledLetters = [];
        for row in self._rows:
            randNum = random.random();
            cdfSoFar = 0;
            for (letterIdx, letterProb) in enumerate(row):
                cdfSoFar += letterProb;
                if (cdfSoFar >= randNum or letterIdx==(len(row)-1)): #need the
                    #letterIdx==(len(row)-1) clause because of floating point errors
                    sampledLetters.append(self.indexToLetter[letterIdx]);
                    break;
        return sampledLetters;
    def __str__(self):
        return self.name+"\n"+str(self._rows); 

def readPwm(fileHandle, pwmFormat=PWM_FORMAT.encodeMotifsFile):
    recordedPwms = OrderedDict();
    currentPwm = util.VariableWrapper(None);
    def action(inp, lineNumber):
        if (inp.startswith(">")):
            inp = inp.lstrip(">");
            inpArr = inp.split();
            motifName = inpArr[0];
            currentPwm.var = PWM(motifName);
            recordedPwms[currentPwm.var.name] = currentPwm.var;
        else:
            #assume that it's a line of the pwm
            assert currentPwm.var is not None;
            inpArr = inp.split();
            summaryLetter = inpArr[0];
            currentPwm.var.addRow([float(x) for x in inpArr[1:]]);
    fp.performActionOnEachLineOfFile(
        fileHandle = fileHandle
        ,transformation=fp.trimNewline
        ,action=action
    );
    for pwm in recordedPwms.values():
        pwm.finalise();
    return recordedPwms;

def scoreSequenceWithPwm(theSeq,pwm):
    scoresArr = [];
    for i in range(len(theSeq)):
        scoresArr.append();
    return scoresArr;

def scorePosWithPwm(theSeq, i, pwm):
    return pwm.scoreSeq(theSeq, i-int(pwm.pwmSize/2), i+(pwm.pwmSize - int(pwm.pwmSize/2))); 

def getSumOfScoresWithPwm(theSeq, pwms):
    pwmScore = OrderedDict();
    for pwm in pwms:
        pwmScore[pwm] = 0.0;
    for i in range(len(theSeq)):
        for pwm in pwms:
            score = scorePosWithPwm(theSeq, i, pwm);
            pwmScore[pwm] += score;
    return pwmScore; 

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser(); 
    parser.add_argument("--pwmFile", required=True);
    args = parser.parse_args();
    pwms = readPwm(fp.getFileHandle(args.pwmFile));
    #print("\n".join([str(x) for x in pwms.values()]));
    theSeq = "ACGATGTAGCCACTGCTGAACATCTGAATATA"; 
    for pwm in pwms.values():
        print(pwm);
        print(pwm.sampleFromPwm());



