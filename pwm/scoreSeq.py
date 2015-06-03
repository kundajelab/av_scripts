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
import argparse;
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
    elif (options.scoreSeqMode in [pwm.SCORE_SEQ_MODE.maxScore, pwm.SCORE_SEQ_MODE.sumScore]):
        return ["score"];
    elif (options.scoreSeqMode==pwm.SCORE_SEQ_MODE.continuous):
        #read the first two lines of the file to determine the len of the sequence.
        seqLen = getLengthOfSequencesByReadingFile(options);
        return ["scoreAtPos"+str(x) for x in xrange(seqLen-options.pwm.pwmSize)];
    else:
        raise RuntimeError("Unsupported score seq mode "+str(options.scoreSeqMode));

def getFileNamePieceFromOptions(options):
    argsToAdd = [util.ArgumentToAdd(options.scoreSeqMode, 'scoreMode')
                ,util.BooleanArgument(options.reverseComplementToo, 'scoreRevToo')]
    toReturn = util.addArguments("", argsToAdd)+pwm.getFileNamePieceFromOptions(options);
    return toReturn;
 
def scoreSeqs(options):
	# For each sequence, record the id, the sequence, the best match to the PWM, and the best match's score
    inputFile = options.fileToScore;
    outputFile= fp.getFileNameParts(inputFile).getFilePathWithTransformation(lambda x: "scoreAdded"+getFileNamePieceFromOptions(options)+"_"+x);
    ofh = fp.getFileHandle(outputFile, 'w');
    thePwm = pwm.getSpecfiedPwmFromPwmFile(options); 
    options.pwm = thePwm;
    def action(inp, lineNumber):
        if (lineNumber==1):
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\t"+("\t".join(getAdditionalColumnTitles(options)))+"\n");
        else:
            seq = inp[options.seqCol];
            scoringResult = thePwm.scoreSeq(seq, options);
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\t"+("\t".join([str(x) for x in scoringResult]))+"\n");
    fp.performActionOnEachLineOfFile(
        fp.getFileHandle(inputFile)
        ,transformation=fp.defaultTabSeppd
        ,action=action
    );
    ofh.close(); 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[pwm.getLoadPwmArgparse()]);
    parser.add_argument("--fileToScore", required=True);
    parser.add_argument("--seqCol", type=int, default=1);
    parser.add_argument("--auxillaryCols", type=int, nargs="+", default=[0,1]);
    parser.add_argument("--scoreSeqMode", choices=pwm.SCORE_SEQ_MODE.vals, required=True);
    parser.add_argument("--reverseComplementToo", action="store_true");
    options = parser.parse_args();
    scoreSeqs(options);

