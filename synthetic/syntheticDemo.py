#!/usr/bin/env python
import synthetic;

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
