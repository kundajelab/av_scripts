#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
from synthetic import synthetic;
import simulationParams_simpleMotifSimulation;

pathToMotifs = simulationParams_simpleMotifSimulation.pathToMotifs;
motif1Name = simulationParams_simpleMotifSimulation.motifName1;
motif2Name = simulationParams_simpleMotifSimulation.motifName2;
seqLength = simulationParams_simpleMotifSimulation.seqLength;
numSeq = simulationParams_simpleMotifSimulation.numSeq;
outputFileName = "descriptiveNameHere_"+motifName+"_seqLength"+str(seqLength)+"_numSeq"+str(numSeq)+".simdata";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001)
embedInBackground = synthetic.EmbedInABackground(
    backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=seqLength) 
    , embedders=[
        synthetic.SubstringEmbedder(
            substringGenerator=synthetic.PwmSamplerFromLoadedMotifs(
               loadedMotifs=loadedMotifs                  
                ,motifName=motifName 
            )
            ,positionGenerator=synthetic.UniformPositionGenerator()  
        )
    ]
);
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);

sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, numSeq)
synthetic.printSequences(outputFileName, sequenceSet);
