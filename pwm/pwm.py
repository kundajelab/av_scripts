#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
import pyximport; pyximport.install()
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
DEFAULT_LETTER_TO_INDEX={'A':0,'C':1,'G':2,'T':3,'N':-1};

SCORE_SEQ_MODE = util.enum(maxScore="maxScore", bestMatch="bestMatch", continuous="continuous", topN="topN");

def getLoadPwmArgparse():
    parser = argparse.ArgumentParser(add_help=False);
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", default="All"); 
    parser.add_argument("--pseudocountProb", type=float, default=0.001); 
    return parser;

def processOptions(options):
    thePwm = pwms
    if options.pwmName != "All":
		# A single PWM has been specified, so get it
        thePwm = getSpecfiedPwmFromPwmFile(options);    
    options.pwm = thePwm;

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.pwmName, 'pwm')
                ,util.ArgumentToAdd(options.pseudocountProb, 'pcPrb')]
    toReturn = util.addArguments("", argsToAdd);
    return toReturn;

def getSpecfiedPwmFromPwmFile(options):
    pwms = readPwm(fp.getFileHandle(options.motifsFile), pseudocountProb=options.pseudocountProb);
    if (options.pwmName not in pwms) and (options.pwmName != "All"):
        raise RuntimeError("pwmName "+options.pwmName+" not in "+options.motifsFile);
    elif (options.pwmName == "All"):
        return pwms
    pwm = [pwms[options.pwmName]]; # List with single PWM    
    return pwm;

def readPwm(fileHandle, pwmFormat=PWM_FORMAT.encodeMotifsFile, pseudocountProb=0.001):
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

class PwmScore(object):
    def __init__(self, score, posStart, posEnd):
        self.score = score;
        self.posStart = posStart;
        self.posEnd = posEnd;
    def __str__(self):
        return str(self.score)+"\t"+str(self.posStart)+"\t"+str(self.posEnd);

class Mutation(object):
    """
        class to represent a single bp mutation in a motif sequence
    """
    def __init__(self, index, previous, new, deltaScore, parentLength=None):
        """
            index: the position within the motif of the mutation
            previous: the previous base at this position
            new: the new base at this position after the mutation
            deltaScore: change in some score corresponding to this mutation change
            parentLength: optional; length of the motif. Used for assertion checks.
        """
        self.index = index;
        assert previous != new;
        self.previous = previous;
        self.new = new;
        self.deltaScore = deltaScore;
        self.parentLength = parentLength; #the length of the full sequence that self.index indexes into
    def parentLengthAssertionCheck(self,stringArr):
        """
            checks that stringArr is consistent with parentLength if defined
        """
        assert self.parentLength is None or len(stringArr)==self.parentLength;
    def revert(self, stringArr):
        """
            set the base at the position of the mutation to the unmutated value
            Modifies stringArr which is an array of characters.
        """
        self.parentLengthAssertionCheck(stringArr);
        stringArr[self.index] = self.previous;
    def applyMutation(self, stringArr):
        """
            set the base at the position of the mutation to the mutated value.
            Modifies stringArr which is an array of characters.
        """
        self.parentLengthAssertionCheck(stringArr);
        assert stringArr[self.index] == self.previous;
        stringArr[self.index] = self.new; 

BEST_HIT_MODE = util.enum(pwmProb="pwmProb", logOdds="logOdds");

class PWM(object):
    def __init__(self, name, letterToIndex=DEFAULT_LETTER_TO_INDEX, background=util.DEFAULT_BACKGROUND_FREQ):
        self.name = name;
        self.letterToIndex = letterToIndex;
        self.indexToLetter = dict((self.letterToIndex[x],x) for x in self.letterToIndex);
        self._rows = [];
        self._rowsRC = [];
        self._finalised = False;
        self.setBackground(background);
    def setBackground(self, background):
        #remember to update everything that might depend on the background!
        self._background = background;
        self._logBackground = dict((x,math.log(self._background[x])) for x in self._background);
        if (self._finalised):
            self.updateBestLogOddsHit();
    def updateBestLogOddsHit(self):
        self.bestLogOddsHit = self.computeBestHitGivenMatrix(self.getLogOddsRows()); 
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
        self._rowsRC = np.fliplr(np.flipud(self._rows)) # ASSUMES THAT THE BASES ARE IN THE FOLLOWING ORDER: A, C, G, T
        self._logRows = np.log(self._rows);
        self._logRowsRC = np.fliplr(np.flipud(self._logRows)) # ASSUMES THAT THE BASES ARE IN THE FOLLOWING ORDER: A, C, G, T
        self._finalised=True; 
        self.bestPwmHit = self.computeBestHitGivenMatrix(self._rows);
        self.updateBestLogOddsHit();
        self.pwmSize = len(self._rows); 
    def getBestHit(self, bestHitMode): # THIS MIGHT NEED TO BE UPDATED FOR RC
        if (bestHitMode == BEST_HIT_MODE.pwmProb):
            return self.bestPwmHit;
        elif (bestHitMode == BEST_HIT_MODE.logOdds):
            return self.bestLogOddsHit;
        else:
            raise RuntimeError("Unsupported bestHitMode "+str(bestHitMode));
    def computeSingleBpMutationEffects(self, bestHitMode):
        if (bestHitMode == BEST_HIT_MODE.pwmProb):
            return self.computeSingleBpMutationEffectsGivenMatrix(self._rows);
        elif (bestHitMode == BEST_HIT_MODE.logOdds):
            return self.computeSingleBpMutationEffectsGivenMatrix(self._logRows);
        else:
            raise RuntimeError("Unsupported best hit mode: "+str(bestHitMode));
    def computeSingleBpMutationEffectsGivenMatrix(self,matrix):
        """
            matrix is some matrix where the rows are positions and the columns represent
            a value for some base at that position, where higher values are more favourable.
            It first finds the best match according to that matrix, and then ranks possible
            deviations from that best match.
        """
        #compute the impact of particular mutations at each position, relative to the best hit
        possibleMutations = [];
        for rowIndex, row in enumerate(matrix):
            bestColIndex = np.argmax(row);
            scoreForBestCol = row[bestColIndex];
            letterAtBestCol = self.indexToLetter[bestColIndex];
            for colIndex,scoreForCol in enumerate(row):
                if (colIndex != bestColIndex):
                    deltaScore = scoreForCol-scoreForBestCol;
                    assert deltaScore <= 0;
                    letter = self.indexToLetter[colIndex];
                    possibleMutations.append(Mutation(index=rowIndex, previous=letterAtBestCol, new=letter, deltaScore=deltaScore, parentLength=self.pwmSize));
        #sort the mutations
        possibleMutations = sorted(possibleMutations, key=lambda x: x.deltaScore); #sorts in ascending order; biggest mutations first
        return possibleMutations;
    def computeBestHitGivenMatrix(self, matrix): 
        return "".join(self.indexToLetter[x] for x in (np.argmax(matrix, axis=1)));
    def getRows(self):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        return self._rows;
		
    def scoreSeqAtPos(self, seqPartIndexes, seqPartBackgroundSum, logRows):
        """
            This method will score the sequence part.
            This behaviour is useful when you want to generate scores at a fixed number
            of positions for a set of PWMs.
			If there is an N anywhere in the sequence (meaning index -1), this will return 0.
			IT ASSUMES THAT ALL LETTERS THAT ARE NOT A, C, G, OR T ARE N's.
			If the reverse complement is being scored, then inputs should be from the reverse complement
			complement of the sequence.
        """
		
        if -1 in seqPartIndexes:
            return 0.0; #return 0 when indicating a segment that is too short or has an N
			# Checking for an N here is faster than checking separately in every iteration, and a score that does not incorporate every base is not very meaningful.
        #cdef float score;
        score = sum(logRows[np.array(range(0, len(seqPartIndexes))), np.array(seqPartIndexes)]) - seqPartBackgroundSum
        return score;
	
    def scoreSeq(self, seq, scoreSeqOptions):
        scoreSeqMode = scoreSeqOptions.scoreSeqMode;
        reverseComplementToo = scoreSeqOptions.reverseComplementToo;
        #cdef float score
        if (scoreSeqMode in [SCORE_SEQ_MODE.maxScore, SCORE_SEQ_MODE.bestMatch]):
            score = -100000000000;
        elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
            toReturn = []; 
        elif (scoreSeqMode == SCORE_SEQ_MODE.topN):
            import heapq;
            heap = [];
            if (scoreSeqOptions.greedyTopN):
                assert len(seq) >= self.pwmSize*scoreSeqOptions.topN;
        else:
            raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);

        #cdef int pos
        #cdef float scoreHere
        seqIndexes = [self.letterToIndex[letter] for letter in seq]
        seqBackgrounds = [self._background[letter] for letter in seq]
        seqPartBackgroundSum = sum(seqBackgrounds[0:self.pwmSize - 1]) # Initializing background sum
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        assert hasattr(self, '_logRows');
        for pos in range(0,len(seq)-self.pwmSize+1):
            seqPartBackgroundSum = seqPartBackgroundSum + seqBackgrounds[pos+self.pwmSize - 1] # Adding next position's background to background sum
            scoreHere = self.scoreSeqAtPos(seqIndexes[pos:pos+self.pwmSize], seqPartBackgroundSum, self._logRows);
            if (reverseComplementToo):
                scoreHere = max(scoreHere, self.scoreSeqAtPos(seqIndexes[pos:pos+self.pwmSize], seqPartBackgroundSum, self._logRowsRC));
            if (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch, SCORE_SEQ_MODE.maxScore]):
                # Get the maximum score
                if scoreHere > score:
                    # The current score is larger than the previous largest score, so store it and the current sequence
                    score = scoreHere;
                    if (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch]):
                        bestMatch = seq[pos:pos+self.pwmSize]
                        bestMatchPosStart = pos;
                        bestMatchPosEnd = pos+self.pwmSize;
            elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
                toReturn.append(scoreHere);
            elif (scoreSeqMode == SCORE_SEQ_MODE.topN):
                heapq.heappush(heap, (-1*scoreHere, scoreHere, pos, pos+self.pwmSize)); #it's a minheap
            else:
                # The current mode is not supported
                raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);
            seqPartBackgroundSum = seqPartBackgroundSum - seqBackgrounds[pos] # Subtracting first position's background from background sum

        if (scoreSeqMode in [SCORE_SEQ_MODE.maxScore]):
            return [score];
        elif (scoreSeqMode in [SCORE_SEQ_MODE.bestMatch]):
            return [bestMatch, score, bestMatchPosStart, bestMatchPosEnd];
        elif (scoreSeqMode in [SCORE_SEQ_MODE.continuous]):
            return toReturn;
        elif (scoreSeqMode == SCORE_SEQ_MODE.topN):
            topNscores = [];
            if (scoreSeqOptions.greedyTopN):
                occupiedHits = np.zeros(len(seq));
            while (len(topNscores) < scoreSeqOptions.topN):
                if (len(heap) > 0):
                    (negScore, score, posStart, posEnd) = heapq.heappop(heap);
                else:
                    (negScore, score, posStart, posEnd) = (0, 0, -1, -1)
                if (not scoreSeqOptions.greedyTopN or np.sum(occupiedHits[posStart:posEnd]) == 0):
                    topNscores.append(PwmScore(score, posStart, posEnd));
                    if (scoreSeqOptions.greedyTopN):
                        occupiedHits[posStart:posEnd] = 1;
            return topNscores;
        else:
            raise RuntimeError("Unsupported score seq mode: "+scoreSeqMode);

    def getLogOddsRows(self):
        toReturn = [];
        for row in self._logRows:
            logOddsRow = [];
            for (i,logVal) in enumerate(row):
                logOddsRow.append(logVal - self._logBackground[self.indexToLetter[i]]);
            toReturn.append(logOddsRow);
        return np.array(toReturn);
    
    def sampleFromPwm(self):
        if (not self._finalised):
            raise RuntimeError("Please call finalised on "+str(self.name));
        sampledLetters = [];
        logOdds = 0;
        for row in self._rows:
            sampledIndex = util.sampleFromProbsArr(row);
            logOdds += math.log(row[sampledIndex]) - self._logBackground[self.indexToLetter[sampledIndex]];
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
    
if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser(); 
    parser.add_argument("--pwmFile", required=True);
    parser.add_argument("--scoreSeqMode", choices=SCORE_SEQ_MODE.vals, required=True, help="The options are: maxScore (just prints out the best score for the motif found in the region), bestMatch (in addition to maxScore, gives the sequence corresponding to the best match), continuous (scores every position in the input sequence), topN (gives the top N scores and their positions; N should be specified using the topN parameter)");
    parser.add_argument("--topN", type=int, help="for when scoreSeqMode is topN; specifies N");
    parser.add_argument("--greedyTopN", action="store_true", help="If enabled, then if scoreSeqMode is topN, will return only non-overlapping topN hits; the hits are determined greedily (that is, first find the best position, then exclude any motif hits that overlap the best hit when determining the second best hit, then exclude anything overlapping both of those when determining the third best hit, and so forth)");
    parser.add_argument("--reverseComplementToo", action="store_true", help="If enabled, will score the reverse complement of the sequence as well.  The output will be the maximum of the score of the sequence and its reverse complement.");
    args = parser.parse_args();
    pwms = readPwm(fp.getFileHandle(args.pwmFile));
    #print("\n".join([str(x) for x in pwms.values()]));
    theSeq = "TACAAAAATTAGGCCAGGTGTCCACCGCGCCCGGCTAATTTTTGTATCTTTTGTAGAGACGGGGTTTCGTCATGTTGCCCAGGCTGGTCTCGAACTCCTGAGCCCAAGCCATCCATCCTCCCGCCTCGGCCTCCCAAAGTGCTGGGATTACAGTAGGGCCCAGCCAGCCTCATGTTTTATTTAGCAGTCCCTCCCTGTTGCACACCTGGA"; 
    for pwm in pwms.values():
        #print(pwm);
        #print(pwm.sampleFromPwm());
        if args.reverseComplementToo:
			# Get the reverse complement
            seqRC = util.reverseComplement(theSeq);
            pwm.scoreSeq(theSeq, args, seqRC);
        else:
			# Get the score with no reverse complement
            pwm.scoreSeq(theSeq, args);



