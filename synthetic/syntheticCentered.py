#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import synthetic;

pathToMotifs = "/scratch/imk1/TFBindingPredictionProject/MotifData/JundSELEXMotif.txt";
outputFileName = "/scratch/imk1/TFBindingPredictionProject/SimulatedData/pos_seqLen1000_bestHit_Jund_positional30_unmodified.txt";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)
embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=1000) 
    , embedders=[
        synthetic.RepeatedEmbedder(
            embedder=synthetic.SubstringEmbedder(
                substringGenerator=synthetic.BestHitPwmFromLoadedMotifs(
                   loadedMotifs=loadedMotifs                  
                    ,motifName="Jund_SELEX"  
                )
                ,positionGenerator=synthetic.InsideCentralBp(30)  
            ),quantityGenerator=synthetic.FixedQuantityGenerator(1) 
        )
    ]
);
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, 10000)
synthetic.printSequences(outputFileName, sequenceSet);
