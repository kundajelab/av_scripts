#!/usr/bin/env python
from __future__ import absolute_import;
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
from pwm import pwm

#where the encode motifs.txt file lives
pathToMotifs = "/Users/avantishrikumar/Research/Enhancer_Prediction/motifs.txt"
motifName = "CTCF_known1"
seqLength = 50
numSeq = 100
positiveSet = True; #boolean indicating if you are making the positive or the negative set
sampleFromPwm = False; #boolean indicating whether to sample from the pwm or use the best hit
bestHitMode = pwm.BEST_HIT_MODE.pwmProb #mode determining how to determine the top N muations and (if sampleFromPwm is false) how to determine the best hit. Options are pwm.BEST_HIT_MODE.pwmProb and pwm.BEST_HIT_MODE.logOdds
topNMutations = 10; #N in top N mutations to consider picking one from; used in generating positive set.
