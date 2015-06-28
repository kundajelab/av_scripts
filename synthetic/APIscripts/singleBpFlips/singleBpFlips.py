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
positiveSet = simulationParams_singleBpFlips.positiveSet;
bestHitMode = simulationParams_singleBpFlips.bestHitMode
topNMutations = simulationParams_singleBpFlips.topNMutations;
outputFileName = "singleBpFlips_"+motifName+"_seqLength"+str(seqLength)+"_bestHitMode-"+bestHitMode+"_topNMutations-"+str(topNMutations)+"_numSeq"+str(numSeq)+"_"+("pos" if positiveSet else "_neg")+".simdata";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)

setOfMutations = synthetic.TopNMutationsFromPwmRelativeToBestHit_FromLoadedMotifs(
    loadedMotifs=loadedMotifs
    ,pwmName = motifName
    ,N = topNMutations 
    ,bestHitMode = bestHitMode
)
transformations=[
    synthetic.RevertToReference(
        setOfMutations=setOfMutations
    ) 
]
if (positiveSet):
    transformations.append(synthetic.ChooseMutationAtRandom(setOfMutations))

embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=seqLength) 
    , embedders=[
        synthetic.SubstringEmbedder(
            substringGenerator=synthetic.TransformedSubstringGenerator(
                substringGenerator=synthetic.PwmSamplerFromLoadedMotifs(
                   loadedMotifs=loadedMotifs                  
                    ,motifName=motifName 
                )
                ,transformations=transformations
            )
            ,positionGenerator=synthetic.UniformPositionGenerator()  
        )
    ]
);
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, numSeq)
synthetic.printSequences(outputFileName, sequenceSet);
