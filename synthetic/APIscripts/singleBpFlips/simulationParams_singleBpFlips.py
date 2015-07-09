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
pathToMotifs = "/scratch/imk1/TFBindingPredictionProject/MotifData/motifs.txt"
motifName = "NFKB_known10"
seqLength = 50
numSeq = 10000
negativeSet = True; #boolean indicating if you are making the positive or the negative set
sampleFromPwm = False; #boolean indicating whether to sample from the pwm or use the best hit
bestHitMode = pwm.BEST_HIT_MODE.logOdds #mode determining how to determine the top N muations and (if sampleFromPwm is false) how to determine the best hit. Options are pwm.BEST_HIT_MODE.pwmProb and pwm.BEST_HIT_MODE.logOdds
topNMutations = 30; #N in top N mutations to consider picking one from; used in generating negative set.
