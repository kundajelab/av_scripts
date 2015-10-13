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
    embedders = [];
    grammarNames = [];
    for aGrammarYamlDict in grammarsYaml:
        if GrammarYamlKeys.grammarName in aGrammarYamlDict:
            grammarName = aGrammarYamlDict[GrammarYamlKeys.grammarName];
        else:
            grammarName = coinGrammarName(aGrammarYamlDict);
        argumentsToAdd = [util.ArgumentToAdd(grammarName, "grammar"), util.BooleanArgument(options.useBestHitForMotifs, "useBestHitForMotifs"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numSeqs, "numSeq")];
        embedders.append(getEmbedderFromGrammarYaml(aGrammarYamlDict, loadedMotifs, options, grammarName=grammarName))
        grammarNames.append(grammarName);
    argumentsToAdd = [util.CoreFileNameArgument(options.grammarsYaml, "grammarsYaml"), util.BooleanArgument(options.useBestHitForMotifs, "useBestHitForMotifs"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numSeqs, "numSeq"), util.ArgumentToAdd(options.meanGrammarsPerSequence, "meanGrammars"), util.ArgumentToAdd(options.maxGrammarsPerSequence, "maxGrammars")];
    outputFileName = util.addArguments("positiveSet",argumentsToAdd)+".simdata";
    quantityGenerator = synthetic.MinMaxWrapper(synthetic.PoissonQuantityGenerator(options.meanGrammarsPerSequence), theMax=options.maxGrammarsPerSequence);
    embedder = synthetic.RandomSubsetOfEmbedders(quantityGenerator=quantityGenerator, embedders=embedders);  
   
    labelGenerator = synthetic.IsInTraceLabelGenerator(grammarNames);
    embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options, options.numSeqs, includeEmbeddings=False, labelGenerator=labelGenerator); 

def doMixtureOfGrammarsSimulation(options):
    grammarsYaml = util.parseYamlFile(options.grammarsYaml);
    print("Loading motifs file: "+str(options.pathToMotifs)); 
    loadedMotifs = getLoadedMotifs(options); 
    for aGrammarYamlDict in grammarsYaml:
        grammarYamlDictIntegrityCheck(aGrammarYamlDict);
    generatePositives(options, grammarsYaml, loadedMotifs);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--pathToMotifs", required=True, help="Path to the file with the pwms");
    parser.add_argument("--pcProb", type=float, default=0.001, help="For encode motif files, no need to modify the default 0.001 pseudocount probability (used to avoid 0 probabilities in pwms");
    parser.add_argument("--grammarsYaml", required=True, help="A yaml file containing all the grammars");
    parser.add_argument("--useBestHitForMotifs", action="store_true");
    parser.add_argument("--seqLen", required=True, type=int);
    parser.add_argument("--numSeqs", type=int, required=True);
    parser.add_argument("--meanGrammarsPerSequence", type=int, required=True);
    parser.add_argument("--maxGrammarsPerSequence", type=int, required=True);
    options = parser.parse_args();
    doMixtureOfGrammarsSimulation(options); 

