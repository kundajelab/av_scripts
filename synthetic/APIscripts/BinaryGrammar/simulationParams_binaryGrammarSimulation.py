import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import util

generationSettings = util.enum(
    allZeros="allZeros" #just strings of all 0's
    ,single1="single1" #string of all 0's with a 1 embedded somewhere at random
    ,twoOnes="twoOnes" #string of all 0's with two 1's embedded somewhere at random
    ,twoOnesFixedSpacing="twoOnesFixedSpacing" #string of all 0's with two 1's that are a fixed spacing apart. Spacing determined by fixedSpacingOrMinSpacing
    ,twoOnesVariableSpacing="twoOnesVariableSpacing" #string of all 0's with two 1's that are a certain range apart. range is fixedSpacingOrMinSpacing to maxSpacing
);

seqLength = 100 #length of the sequences
numSeq = 100 #total number of sequences generated
generationSetting = generationSettings.twoOnesVariableSpacing;
fixedSpacingOrMinSpacing = 10;
maxSpacing=20;
