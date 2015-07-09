#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
from synthetic import synthetic;
import simulationParams_singleBpFlips;

pathToMotifs = simulationParams_singleBpFlips.pathToMotifs;
motifName = simulationParams_singleBpFlips.motifName;
seqLength = simulationParams_singleBpFlips.seqLength;
numSeq = simulationParams_singleBpFlips.numSeq;
#negativeSet is a boolean indicating whether you are generating the positive or the negative set
negativeSet = simulationParams_singleBpFlips.negativeSet;
#sampleFromPwm is True if you want to sample from the pwm, and false if you only want to use the best hit. The framework for defining the best hit (using the PWM or using the log odds matrix) is determined by bestHitMode below, which is ALSO used to determine how to define the top N mutations.
sampleFromPwm = simulationParams_singleBpFlips.sampleFromPwm;
#bestHitMode is from pwm.BEST_HIT_MODE; it is either pwm.BEST_HIT_MODE.pwmProb or pwm.BEST_HIT_MODE.logOdds, and determines whether the top N mutations are defined using the pwm probability matrix or the log odds matrix (the latter basically also accounts for the frequencies of the bases in the background; the background defaults to 40% GC content which seems about right for human chromosomes)
bestHitMode = simulationParams_singleBpFlips.bestHitMode
#topNMutations is an integer; one mutation from the top N will be randomly picked and applied in the negative set; in the positive set, all positions corresponding to the top N mutations will be set to what they are in the best hit. To clarify, if you are sampling from the pwm, then the positions that correspond to the top N mutations will NOT be subject to sampling; it will only apply to positions outside the top N.
topNMutations = simulationParams_singleBpFlips.topNMutations;

outputFileName = "singleBpFlips_"+motifName+"_seqLength"+str(seqLength)+"_"+("sampled" if sampleFromPwm else "bestHit")+"_bestHitMode-"+bestHitMode+"_topNMutations-"+str(topNMutations)+"_numSeq"+str(numSeq)+"_"+("neg" if negativeSet else "neg")+".simdata";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)

#creates the set of the top N mutations
setOfMutations = synthetic.TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs(
    loadedMotifs=loadedMotifs
    ,pwmName = motifName
    ,N = topNMutations 
    ,bestHitMode = bestHitMode
)

#if sampleFromPwm is true, will sample from the pwm originally; otherwise will just use the best hit
if (sampleFromPwm):
    substringGenerator = synthetic.PwmSamplerFromLoadedMotifs(
       loadedMotifs=loadedMotifs                  
        ,motifName=motifName 
    )
else:
    substringGenerator = synthetic.BestHitPwmFromLoadedMotifs(
        loadedMotifs=loadedMotifs
        ,motifName=motifName
        ,bestHitMode=bestHitMode
    );

#transformations is the array of transformations to be applied after the substring (in this case motif) to be embedded has been generated (using the class above; either the best hit or a sampling from the pwm is performed)
transformations=[
    #the "RevertToReference" transformation makes sure that all the positions corresponding to the mutations are set to what they are in the best hit. If substringGenerator is a BestHit generator to begin with, this transformation does not end up doing anything. In the negative set, this is the only transformation you apply. In the negative set, you follow this up with a transformation that applies one of the top N mutations, as you will see below.
    synthetic.RevertToReference(
        setOfMutations=setOfMutations
    ) 
]
if (negativeSet): #if you are generating the negative set
    #also apply a transformation which chooses from the top N mutations and applies one at random.
    transformations.append(synthetic.ChooseMutationAtRandom(setOfMutations))


embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=seqLength) 
    , embedders=[
        synthetic.SubstringEmbedder(
            #TransformedSubstingGenerator takes a substringGenerator and also an array of transformations to apply, and applies the transformations.
            substringGenerator=synthetic.TransformedSubstringGenerator(
                substringGenerator=substringGenerator
                ,transformations=transformations
            )
            ,positionGenerator=synthetic.UniformPositionGenerator()  
        )
    ]
);
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, numSeq)
synthetic.printSequences(outputFileName, sequenceSet);
