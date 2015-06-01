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

def scoreSeqs(options):
	# For each sequence, record the id, the sequence, the best match to the PWM, and the best match's score
    inputFile = options.fileToScore;
    outputFile= fp.getFileNameParts(inputFile).getFilePathWithTransformation(lambda x: "scoreAdded_"+options.pwmName+"_"+x);
    ofh = fp.getFileHandle(outputFile, 'w');
    thePwm = pwm.getSpecfiedPwmFromPwmFile(options); 
    def action(inp, lineNumber):
        if (lineNumber==1):
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\tbest match\tscore\n");
        else:
            seq = inp[options.seqCol];
            [bestMatch, score] = thePwm.scoreSeq(seq, scoreSeqMode="bestMatch");
            ofh.write("\t".join(inp[x] for x in options.auxillaryCols)+"\t" + bestMatch + "\t" +str(score)+"\n");
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
    options = parser.parse_args();
    scoreSeqs(options);

