
#arguments --> object
#

class ArgumentsHandler(object):
    def parseArgparseCheckArgsGetArgsToAddCallFunction(self, args):
        """
            return args to add and the result of the function in question
        """
    def getArgumentsToAdd(self, options):

class Template(object):
    def applyArgparseToAugmentOptionsObject(args, previousOptions):
        """
            Will apply instance-specific argparse to args
            to generate an object with everything necessary for options
            Creates a new object with the new options added, returns it
        """
    def getObject(self, options):
        """
           Get an object that uses the options 
        """
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

