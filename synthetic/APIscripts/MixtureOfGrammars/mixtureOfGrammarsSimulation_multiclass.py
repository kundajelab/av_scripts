#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
sys.path.insert(0,scriptsDir+"/synthetic/APIscripts/");
sys.path.insert(0,scriptsDir+"/synthetic/APIscripts/MixtureOfGrammars");
import pathSetter
from synthetic import synthetic;
import util;
from pwm import pwm;
from apiHelperFunctions import getLoadedMotifs, getMotifGenerator; 
from mixtureOfGrammarsSimulationMethods import getEmbedderFromGrammarYaml, grammarYamlDictIntegrityCheck, coinGrammarName, embedInABackgroundAndGenerateSeqs, GrammarYamlKeys;

def generatePositives(options, grammarsYaml, loadedMotifs):
    print("Generating positives");
    for aGrammarYamlDict in grammarsYaml:
        if GrammarYamlKeys.grammarName in aGrammarYamlDict:
            grammarName = aGrammarYamlDict[GrammarYamlKeys.grammarName];
        else:
            grammarName = coinGrammarName(aGrammarYamlDict);
        print("Generating "+grammarName);
        argumentsToAdd = [util.ArgumentToAdd(grammarName, "grammar"), util.BooleanArgument(options.useBestHitForMotifs, "useBestHitForMotifs"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numPositiveSeqsPerGrammar, "numSeq")];
        outputFileName = util.addArguments("positiveSet",argumentsToAdd)+".simdata";
        embedder = getEmbedderFromGrammarYaml(aGrammarYamlDict, loadedMotifs, options);  
        embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options, options.numPositiveSeqsPerGrammar); 

def generateNegatives(options, grammarsYaml, loadedMotifs):
    print("Generating negatives");
    if options.numNegativeSeqs is None:
        options.numNegativeSeqs = options.numPositiveSeqsPerGrammar*len(grammarsYaml);
    from collections import OrderedDict;
    appearingMotifsDict = OrderedDict();
    #compile the set of motifs that appear
    for aGrammarYamlDict in grammarsYaml:
        for key in [GrammarYamlKeys.motif1, GrammarYamlKeys.motif2]:
            appearingMotifsDict[aGrammarYamlDict[key]] = 1;
    appearingMotifs = appearingMotifsDict.keys();
    print("Appearing motifs: "+", ".join(appearingMotifs));
    motifEmbedders = [synthetic.EmbeddableEmbedder(embeddableGenerator=synthetic.SubstringEmbeddableGenerator(getMotifGenerator(motifName, loadedMotifs, options))) for motifName in appearingMotifs];
    quantityGenerator = synthetic.MinMaxWrapper(synthetic.PoissonQuantityGenerator(options.meanMotifsInNegative), theMax=options.maxMotifsInNegative);
    embedder = synthetic.RandomSubsetOfEmbedders(quantityGenerator=quantityGenerator, embedders=motifEmbedders);  
    argumentsToAdd = [util.CoreFileNameArgument(options.grammarsYaml, "grammarsYaml"), util.BooleanArgument(options.useBestHitForMotifs, "useBestHitForMotifs"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numNegativeSeqs, "numSeq"), util.ArgumentToAdd(options.meanMotifsInNegative, "meanMotifs"), util.ArgumentToAdd(options.maxMotifsInNegative, "maxMotifs")];
    outputFileName = util.addArguments("negativeSet",argumentsToAdd)+".simdata";
    embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options, options.numNegativeSeqs);

def doMixtureOfGrammarsSimulation(options):
    grammarsYaml = util.parseYamlFile(options.grammarsYaml);
    print("Loading motifs file: "+str(options.pathToMotifs)); 
    loadedMotifs = getLoadedMotifs(options); 
    for aGrammarYamlDict in grammarsYaml:
        grammarYamlDictIntegrityCheck(aGrammarYamlDict);
    generatePositives(options, grammarsYaml, loadedMotifs);
    generateNegatives(options, grammarsYaml, loadedMotifs);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--pathToMotifs", required=True, help="Path to the file with the pwms");
    parser.add_argument("--pcProb", type=float, default=0.001, help="For encode motif files, no need to modify the default 0.001 pseudocount probability (used to avoid 0 probabilities in pwms");
    parser.add_argument("--grammarsYaml", required=True, help="A yaml file containing all the grammars");
    parser.add_argument("--useBestHitForMotifs", action="store_true");
    parser.add_argument("--seqLen", required=True, type=int);
    parser.add_argument("--numPositiveSeqsPerGrammar", type=int, required=True);
    parser.add_argument("--numNegativeSeqs", type=int, help="If not specified, will default to equal total size of positive set");
    parser.add_argument("--meanMotifsInNegative", type=int, default=2, help="Defaults to 2; poission sampled");
    parser.add_argument("--maxMotifsInNegative", type=int, default=4, help="Defaults to 4");
    options = parser.parse_args();
    doMixtureOfGrammarsSimulation(options); 

