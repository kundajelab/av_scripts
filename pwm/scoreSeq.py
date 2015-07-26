#!/usr/bin/env python
from __future__ import absolute_import;
from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import argparse;
import numpy as np;
from pwm import pwm;
import fileProcessing as fp;

def getLengthOfSequencesByReadingFile(options):
    tempofh = fp.getFileHandle(options.fileToScore);
    line = tempofh.readline();
    line = tempofh.readline(); #read the first 2 lines
    line = line.rstrip();
    arr = line.split("\t");
    seq = arr[options.seqCol];
    seqLen = len(seq); 
    tempofh.close();
    return seqLen; 

def getAdditionalColumnTitles(options):
    if (options.scoreSeqMode==pwm.SCORE_SEQ_MODE.bestMatch):
        return ["bestMatch","score", "bestMatchStartPos", "bestMatchEndPos"];
    elif (options.scoreSeqMode in [pwm.SCORE_SEQ_MODE.maxScore]):
        return ["score"];
    elif (options.scoreSeqMode==pwm.SCORE_SEQ_MODE.continuous):
        #read the first two lines of the file to determine the len of the sequence.
        seqLen = getLengthOfSequencesByReadingFile(options);
        return ["scoreAtPos"+str(x) for x in xrange(seqLen-options.pwm.pwmSize)];
    elif (options.scoreSeqMode==pwm.SCORE_SEQ_MODE.topN):
        tuples = [("top"+str(x)+"Score","top"+str(x)+"StartPos","top"+str(x)+"EndPos") for x in range(1,options.topN+1)];
        toReturn = [];
        for atuple in tuples:
            toReturn.extend(atuple);
        return toReturn;
    else:
        raise RuntimeError("Unsupported score seq mode "+str(options.scoreSeqMode));

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.scoreSeqMode, 'scrMd')
                ,util.ArgumentToAdd(options.topN, 'top')
                ,util.BooleanArgument(options.greedyTopN, 'greedy')
                ,util.BooleanArgument(options.reverseComplementToo, 'scrRvToo')]
    toReturn = util.addArguments("", argsToAdd)+pwm.getFileNamePieceFromOptions(options);
    return toReturn;
 
def scoreSeqs(options,returnScores=True):
	# For each sequence, record the id, the sequence, the best match to the PWM, and the best match's score
    inputFile = options.fileToScore;
    outputFile= fp.getFileNameParts(inputFile).getFilePathWithTransformation(lambda x: "scoreAdded"+getFileNamePieceFromOptions(options)+"_"+x);
    ofh = fp.getFileHandle(outputFile, 'w');
    thePwm = pwm.getSpecfiedPwmFromPwmFile(options); 
    options.pwm = thePwm;
    if (returnScores):
        scoringResultList = []; # The scores are stored here
        positionResultList = []; # The centers of the top motifs are stored here
    def action(inp, lineNumber):
        if (lineNumber==1):
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\t"+("\t".join(getAdditionalColumnTitles(options)))+"\n");
        else:
            seq = inp[options.seqCol];
            scoreInfoList = thePwm.scoreSeq(seq, options);
            if (returnScores):
                scoringResult = []
                positionResult = []
                for scoreInfo in scoreInfoList:
                    # Iterate through the top PWMs and get the score for each
                    scoringResult.append(scoreInfo.score)
                    positionResult.append(int(round(float(scoreInfo.posEnd - scoreInfo.posStart)/float(2)))) # Computing the locations of the motif centers
                scoringResultList.append(np.array(scoringResult))
                positionResultList.append(np.array(positionResult))
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\t"+("\t".join([str(x) for x in scoreInfoList]))+"\n");
    fp.performActionOnEachLineOfFile(
        fp.getFileHandle(inputFile)
        ,transformation=fp.defaultTabSeppd
        ,action=action
    );
    ofh.close();
    if (returnScores): 
        return [np.asarray(scoringResultList), np.asarray(positionResultList)];

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--motifsFile", required=True, help="The file with the motifs - the file I've been using is called motifs.txt and contains Pouya's encode motifs");
    parser.add_argument("--pwmName", required=True, help="The name of the pwm in the file specified in motifsFile, eg: CTCF_known1"); 
    parser.add_argument("--pseudocountProb", type=float, default=0.001, help="Pouya's encode motifs file has a probability of 0 in some positions. The value specified here is used to pseudocount the pwm so that there are no zero probabilities; it defaults to 0.001 which is what I've used for Pouya's motifs"); 
    parser.add_argument("--fileToScore", required=True, help="The file that you want to score. Is expected to have a title line and be tab separated");
    parser.add_argument("--seqCol", type=int, default=1, help="The column storing the sequence in the file you want to score. Defaults to 1 (0-based indexed");
    parser.add_argument("--auxillaryCols", type=int, nargs="+", default=[0,1], help="Any columns in the input that you would like to retain in the output should be specified here, separated by spaces; defaults to 0 1");
    parser.add_argument("--scoreSeqMode", choices=pwm.SCORE_SEQ_MODE.vals, required=True, help="The options are: maxScore (just prints out the best score for the motif found in the region), bestMatch (in addition to maxScore, gives the sequence corresponding to the best match), continuous (scores every position in the input sequence), topN (gives the top N scores and their positions; N should be specified using the topN parameter)");
    parser.add_argument("--topN", type=int, help="for when scoreSeqMode is topN; specifies N");
    parser.add_argument("--greedyTopN", action="store_true", help="If enabled, then if scoreSeqMode is topN, will return only non-overlapping topN hits; the hits are determined greedily (that is, first find the best position, then exclude any motif hits that overlap the best hit when determining the second best hit, then exclude anything overlapping both of those when determining the third best hit, and so forth");
    parser.add_argument("--reverseComplementToo", action="store_true", help="If enabled, will score the reverse complement of the sequence as well");
    options = parser.parse_args();
    if (options.greedyTopN):
        if (options.topN is None):
            raise RuntimeError("topN should not be none if greedyTopN flag is specified");
    scoreSeqs(options, returnScores=False);

