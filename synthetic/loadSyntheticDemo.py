#!/usr/bin/env python
import synthetic;
pathToMotifs = "motifs.txt";
loadedMotifs = synthetic.LoadedEncodeMotifs(pathToMotifs, pseudocountProb=0.001);
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
            ,quantityGenerator=synthetic.MinMaxWrapper(quantityGenerator=synthetic.PoissonQuantityGenerator(3),theMin=1,theMax=5) 
        )
        ,
        synthetic.RepeatedEmbedder(
            embedder=synthetic.SubstringEmbedder(
                substringGenerator=synthetic.PwmSamplerFromLoadedMotifs(
                   loadedMotifs=loadedMotifs 
                    ,motifName="SPI1_known1"  
                )
                ,positionGenerator=synthetic.OutsideCentralBp(400)  
            )
            ,quantityGenerator=synthetic.FixedQuantityGenerator(1) 
        )
    ]
);

generatedSeq=embedInBackground.generateSequence();
print generatedSeq.seq,"\n", generatedSeq.seqName,"\n", [(x.seq, x.startPos) for x in generatedSeq.embeddings]
