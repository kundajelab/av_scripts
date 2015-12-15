import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import util
from pwm import pwm;

pathToMotifs="/Users/avantishrikumar/Research/Enhancer_Prediction/motifs.txt";
motifName1="CTCF_known1";
motifName2="IRF_known1";
bestHit=True #if true, will use the besthit matches to the pwm
bestHitMode=pwm.BEST_HIT_MODE.pwmProb; #prob don't need to twiddle this
seqLength = 100 #length of the sequences
numSeq = 100 #total number of sequences generated
generationSetting = generationSettings.twoMotifsVariableSpacing;
fixedSpacingOrMinSpacing = 10;
maxSpacing=20;

