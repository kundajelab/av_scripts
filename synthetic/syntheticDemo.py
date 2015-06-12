#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
from synthetic import synthetic;

pathToMotifs = "motifs.txt";
outputFileName = "descriptiveNameHere.txt";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)
embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=500) 
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

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, 10)
synthetic.printSequences(outputFileName, sequenceSet);
