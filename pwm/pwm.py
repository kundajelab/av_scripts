from __future__ import divison;
from __future__ import print_function;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import np;
import math;
import random;

PWM_FORMAT = util.enum(encodeMotifsFile="encodeMotifsFile");

def PWM(object):
    def __init__(name, letterToIndex):
        self.name = name;
        self.letterToIndex = letterToIndex;
        self.indexToLetter = dict((self.letterToIndex[x],x) for x in self.letterToIndex);
        self._rows = [];
        self._finalsed = False;
    def addRow(weights):
        if (len(self._rows) > 0):
            assert len(weights) == len(self._rows[0]);
        self._rows.append(weights);
    def finalise(pseudocountProb):
        assert pseudocountProb >= 0 and pseudocountProb < 1;
        #will smoothen the rows with a pseudocount...
        self._rows = np.array(self.rows);
        self._rows = self._rows*(1-pseudocountSize) + float(pseudocountSize)/len(_rows[0]);
        for row in self._rows:
            assert sum(row) == 1;
        self.logRows = np.log(self_rows);
        self._finalised=True;  
    def getRows(self);
        if (!self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        return self._rows;
    def scoreSeq(seq, background={'A':0.3,'C':0.2,'G':0.2,'T':0.3):
        if (!self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        assert hasattr(self, 'logRows');
        assert len(seq)==len(self.logRows); 
        score = 0;
        self.logBackground = dict((x,math.log(background[x])) for x in background);
        for idx,letter in enumerate(seq):  
            if (letter not in self.letterToIndex and (letter=='N' or letter=='n')):
                pass; #just skip the letter
            else:
                score += self.logRows[idx, self.letterToIndex[letter]] - self.logBackground[letter];
        return score;
    def sampleFromPwm(self):
        if (!self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        sampledLetters = [];
        for row in self._rows:
            randNum = random.random();
            cdfSoFar = 0;
            for (letterIdx, letterProb) in enumerate(row):
                cdfSoFar += letterProb;
                if (cdfSoFar >= randNum):
                    sampledLetters.append(self.indexToLetter[letterIdx]);
                    break;
            if cdfSoFar != 1.0:
                print(row);
                raise RuntimeError("Probs don't sum to 1!");
        return sampledLetters; 

def readPwm(fileHandle, pwmFormat=PWM_FORMAT.encodeMotifsFile):
    recordedPwms = {};
    currentPwm = util.VariableWrapper(None);
    def action(inp, lineNumber):
        if (inp.startsWith(">")):
            inp = inp.lstrip(">");
            inpArr = inp.split("\s");
            motifName = inpArr[0];
            currentPwm.var = PWM(motifName);
            recordedPwms[currentPwm.var.name] = currentPwm;
        else:
            #assume that it's a line of the pwm
            assert currentPwm.var is not None;
            inpArr = inp.split("\s");
            summaryLetter = inpArr[0];
            currentPwm.var.rows.append(inpArr[1:]);
    fp.performActionOnEachLinOfFile(
        fileHandle = fileHandle
        ,transformation=fp.trimNewline
        ,action=action
    );
    return recordedPwms; 
