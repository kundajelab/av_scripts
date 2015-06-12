

class Template(object):
    def requiredAttributes(self):
        raise NotImplementedError();
    def getSequenceGenerator(self, options):
        raise NotImplementedError();

class NSequencesTemplate(object):
    def requiredAttributes(self):
        return ['numSeq']+self.getAdditionalRequiredForSingleSequence();
    

    def getRequiredAttributesForSingleSequence(self):
        raise NotImplementedError();
    def getSingleSequenceGenerator():
        raise NotImplementedError();

def zeroInflatedBackground(options,loadedMotifs):
    """
        requires: options.motifName, options.zeroProb, options.seqLength
    """
    toReturn = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(seqLength=500) 
        , embedders=[
            synthetic.RepeatedEmbedder(
                embedder=synthetic.SubstringEmbedder(
                    substringGenerator=synthetic.PwmSamplerFromLoadedMotifs(
                       loadedMotifs=loadedMotifs                  
                        ,motifName=options.motifName 
                    )
                    ,positionGenerator=synthetic.UniformPositionGenerator()  
                )
                ,quantityGenerator=
                    synthetic.ZeroInflater(
                        zeroProb: options.zeroProb
                        ,synthetic.MinMaxWrapper(synthetic.PoissonQuantityGenerator(1),theMax=2)
                ) 
            )
        ]
    );
    return toReturn;

