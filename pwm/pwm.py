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
import argparse;
from collections import OrderedDict;

PWM_FORMAT = util.enum(encodeMotifsFile="encodeMotifsFile", singlePwm="singlePwm");
DEFAULT_LETTER_TO_INDEX={'A':0,'C':1,'G':2,'T':3};

SCORE_SEQ_MODE = util.enum(maxScore="maxScore", bestMatch="bestMatch", continuous="continuous");

def getLoadPwmArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", required=True); 
    parser.add_argument("--pseudocountProb", type=float, default=0.0); 
    return parser;

def processOptions(options):
    thePwm = getSpecfiedPwmFromPwmFile(options);    
    options.pwm = thePwm;

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.pwmName, 'pwm')
                ,util.ArgumentToAdd(options.pseudocountProb, 'pcProb')]
    toReturn = util.addArguments("", argsToAdd);
    return toReturn;

def getSpecfiedPwmFromPwmFile(options):
    pwms = readPwm(fp.getFileHandle(options.motifsFile), pseudocountProb=options.pseudocountProb);
    if options.pwmName not in pwms:
        raise RuntimeError("pwmName "+options.pwmName+" not in "+options.motifsFile); 
    pwm = pwms[options.pwmName];    
    return pwm;

def readPwm(fileHandle, pwmFormat=PWM_FORMAT.encodeMotifsFile, pseudocountProb=0.0):
    recordedPwms = OrderedDict();
    if (pwmFormat == PWM_FORMAT.encodeMotifsFile):
        action = getReadPwmAction_encodeMotifs(recordedPwms);
    else:
        raise RuntimeError("Unsupported pwm format: "+str(pwmFormat));
    fp.performActionOnEachLineOfFile(
        fileHandle = fileHandle
        ,transformation=fp.trimNewline
        ,action=action
    );
    for pwm in recordedPwms.values():
        pwm.finalise(pseudocountProb=pseudocountProb);
    return recordedPwms;

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
        self.bestHit = "".join(self.indexToLetter[x] for x in (np.argmax(self._rows, axis=1)));
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
    def scoreSeqAtPos(self, seq, startIdx, background=util.DEFAULT_BACKGROUND_FREQ):
        """
            This method will score the seq at startIdx:startIdx+len(seq).
            if startIdx is < 0 or startIdx is too close to the end of the string,
            returns 0.
            This behaviour is useful when you want to generate scores at a fixed number
            of positions for a set of PWMs, some of which are longer than others.
            So at each position, for startSeq you supply pos-len(pwm)/2, and if it
            does not fit the score will automatically be 0. 
        """
        endIdx = startIdx+self.pwmSize;
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        assert hasattr(self, 'logRows');
        if (endIdx > len(seq) or startIdx < 0):
            return 0.0; #return 0 when indicating a segment that is too short
        score = 0;
        logBackground = dict((x,math.log(background[x])) for x in background);
        for idx in xrange(startIdx, endIdx):
            letter = seq[idx];
            if (letter not in self.letterToIndex and (letter=='N' or letter=='n')):
                pass; #just skip the letter
            else:
                #compute the score at this position
                score += self.logRows[idx-startIdx, self.letterToIndex[letter]] - logBackground[letter]
        return score;
    
    def scoreSeq(self, seq, scoreSeqMode=SCORE_SEQ_MODE.bestMatch, background=util.DEFAULT_BACKGROUND_FREQ):
        # This finds the best score and the subsequence with that score
        bestMatch = ""
        if (scoreSeqMode in [SCORE_SEQ_MODE.maxScore, SCORE_SEQ_MODE.bestMatch]):
            score = -100000000000;
        elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
            toReturn = []; 
        else:
            raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);

        for pos in range(0,len(seq)-self.pwmSize+1):
            scoreHere = self.scoreSeqAtPos(seq, pos, background=background);
            if (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch, SCORE_SEQ_MODE.maxScore]):
                # Get the maximum score
                if scoreHere > score:
                    # The current score is larger than the previous largest score, so store it and the current sequence
                    score = scoreHere;
                    if (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch]):
                        bestMatch = seq[pos:pos+self.pwmSize]
            elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
                toReturn.append(scoreHere); 
            else:
                # The current mode is not supported
                raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);

        if (scoreSeqMode in [SCORE_SEQ_MODE.maxScore]):
            return [score];
        elif (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch]):
            return [bestMatch, score];
        elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
            return toReturn;
        else:
            raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);

    def getLogOddsRows(self, background=util.DEFAULT_BACKGROUND_FREQ):
        logBackground = dict((x,math.log(background[x])) for x in background);
        toReturn = [];
        for row in self.logRows:
            logOddsRow = [];
            for (i,logVal) in enumerate(row):
                logOddsRow.append(logVal - logBackground[self.indexToLetter[i]]);
            toReturn.append(logOddsRow);
        return np.array(toReturn);
    
    def sampleFromPwm(self, background=util.DEFAULT_BACKGROUND_FREQ):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        sampledLetters = [];
        logOdds = 0;
        self.logBackground = dict((x,math.log(background[x])) for x in background); 
        for row in self._rows:
            sampledIndex = util.sampleFromProbsArr(row);
            logOdds += math.log(row[sampledIndex]) - self.logBackground[self.indexToLetter[sampledIndex]];
            sampledLetters.append(self.indexToLetter[util.sampleFromProbsArr(row)]);
        return "".join(sampledLetters), logOdds;
    def __str__(self):
        return self.name+"\n"+str(self._rows); 


def getReadPwmAction_encodeMotifs(recordedPwms):
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
    return action;
    
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



