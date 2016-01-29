#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import util;
from synthetic import synthetic as sn;
import argparse;

def getEmbedder(motifs, constructor, loadedMotifs, numDistinctPerSeq, theMean, theMax, theMin):
    return sn.RandomSubsetOfEmbedders(
        quantityGenerator=sn.FixedQuantityGenerator(numDistinctPerSeq) 
        ,embedders=[
            sn.RepeatedEmbedder( 
                embedder=sn.SubstringEmbedder(
                            substringGenerator=constructor(
                                loadedMotifs=loadedMotifs
                                , motifName=motifName))
                ,quantityGenerator=sn.MinMaxWrapper(
                    sn.PoissonQuantityGenerator(mean=theMean)
                    ,theMax=theMax, theMin=theMin)
            ) for motifName in motifs
        ]
    )

def do(options):
    outputFileName_core = util.addArguments("FilterDiversityPosSet", [
                                                 util.ArgumentToAdd(options.seqLength, "seqLength")
                                                 ,util.ArgumentToAdd(options.numSeqs, "numSeqs")
                                                 ,util.BooleanArgument(options.bestHit, "bestHit")
                                                 #,util.ArrArgument(options.freqMotifs, "freqMotifs")
                                                 ,util.ArgumentToAdd(options.freqMoMean, "freqMoMean")
                                                 ,util.ArgumentToAdd(options.freqMoMax, "freqMoMax")
                                                 ,util.ArgumentToAdd(options.freqMoMin, "freqMoMin")
                                                 #,util.ArrArgument(options.infreqMotifs, "infreqMotifs")
                                                 ,util.ArgumentToAdd(options.infreqMoMean, "infreqMoMean")
                                                 ,util.ArgumentToAdd(options.infreqMoMax, "infreqMoMax")
                                                 ,util.ArgumentToAdd(options.infreqMoMin, "infreqMoMin")
                                                 ]);
    
    loadedMotifs = sn.LoadedEncodeMotifs(options.pathToMotifs, pseudocountProb=0.001)
    Constructor = sn.BestHitPwmFromLoadedMotifs if options.bestHit else sn.PwmSamplerFromLoadedMotifs;  
 
    embedInBackground = sn.EmbedInABackground(
        backgroundGenerator=sn.ZeroOrderBackgroundGenerator(seqLength=options.seqLength) 
        , embedders=[
            getEmbedder(motifs=options.freqMotifs
                        , constructor=Constructor
                        , loadedMotifs=loadedMotifs
                        , numDistinctPerSeq=1
                        , theMean=options.freqMoMean
                        , theMax=options.freqMoMax
                        , theMin=options.freqMoMin)
            ,getEmbedder(motifs=options.infreqMotifs
                        , constructor=Constructor
                        , loadedMotifs=loadedMotifs
                        , numDistinctPerSeq=1
                        , theMean=options.infreqMoMean
                        , theMax=options.infreqMoMax
                        , theMin=options.infreqMoMin)
        ]
    );
    sequenceSet = sn.GenerateSequenceNTimes(embedInBackground, options.numSeqs)
    sn.printSequences(outputFileName_core+".simdata", sequenceSet, includeFasta=True, includeEmbeddings=True);
   
if __name__=="__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--pathToMotifs", default="motifs.txt");
    parser.add_argument("--bestHit", action="store_true");
    parser.add_argument("--freqMotifs", nargs='+', required=True);
    parser.add_argument("--freqMoMax",type=int, required=True);
    parser.add_argument("--freqMoMin",type=int, required=True);
    parser.add_argument("--freqMoMean",type=int, required=True);
    parser.add_argument("--infreqMotifs", nargs='+', required=True);
    parser.add_argument("--infreqMoMax",type=int, required=True);
    parser.add_argument("--infreqMoMin",type=int, required=True);
    parser.add_argument("--infreqMoMean",type=int, required=True);
    parser.add_argument("--seqLength", type=int, required=True);
    parser.add_argument("--numSeqs", type=int, required=True);
    options = parser.parse_args();
    do(options);     
