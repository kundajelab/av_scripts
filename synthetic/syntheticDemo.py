#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import synthetic;

pathToMotifs = "/scratch/imk1/TFBindingPredictionProject/MotifData/motifs.txt";
outputFileName = "/scratch/imk1/TFBindingPredictionProject/SimulatedData/neg_seqLen1000_pwm_multi_unmodified.txt";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)
embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=1000) 
    , embedders=[
        synthetic.RepeatedEmbedder(
            embedder=synthetic.SubstringEmbedder(
                substringGenerator=synthetic.PwmSamplerFromLoadedMotifs(
                   loadedMotifs=loadedMotifs                  
                    ,motifName="CTCF_known1"  
                )
                ,positionGenerator=synthetic.UniformPositionGenerator()  
            )
            ,quantityGenerator=
                synthetic.ZeroInflater(
                    synthetic.MinMaxWrapper(synthetic.PoissonQuantityGenerator(1),theMax=2)
                    ,zeroProb=0.75
            ) 
        )
    ]
);
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, 10000)
synthetic.printSequences(outputFileName, sequenceSet);
