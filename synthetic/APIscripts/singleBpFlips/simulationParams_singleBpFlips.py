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

pathToMotifs = "/Users/avantishrikumar/Research/Enhancer_Prediction/motifs.txt"
motifName = "CTCF_known1"
seqLength = 50
numSeq = 100
positiveSet = True;
sampleFromPwm = False;
bestHitMode = pwm.BEST_HIT_MODE.pwmProb #pwm.BEST_HIT_MODE.logOdds
topNMutations = 10;
