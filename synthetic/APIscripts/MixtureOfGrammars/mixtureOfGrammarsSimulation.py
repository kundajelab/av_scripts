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
import pathSetter
from synthetic import synthetic;
import util;
from pwm import pwm;

GrammarYamlKeys = util.enum(motif1="motif1",motif2="motif2",spacingSetting="spacingSetting",grammarName="grammarName");
SpacingSettings = util.enum(fixedSpacing="fixedSpacing", variableSpacing="variableSpacing");
GrammarYamlKeys_fixedSpacing = util.enum(fixedSpacingValues="fixedSpacingValues"); #keys applicable to the case of fixedSpacing
GrammarYamlKeys_variableSpacing = util.enum(minimum="minimum", maximum="maximum"); #keys applicable to the case of variable spacing

def getLoadedMotifs(options):
    loadedMotifs = synthetic.LoadedEncodeMotifs(options.pathToMotifs, pseudocountProb=options.pcProb)
    return loadedMotifs;

def getMotifGenerator(motifName, loadedMotifs, options):
    kwargs={'loadedMotifs':loadedMotifs}
    if (options.useBestHitForMotifs):
        theClass=synthetic.BestHitPwmFromLoadedMotifs;
        kwargs['bestHitMode']=bestHitMode=pwm.BEST_HIT_MODE.pwmProb; #prob don't need to twiddle this
    else:
        theClass=synthetic.PwmSamplerFromLoadedMotifs;
    motifGenerator=theClass(motifName=motifName,**kwargs)
    return motifGenerator;

def getEmbedderFromGrammarYaml(aGrammarYamlDict, loadedMotifs, options):
    """
        aGrammarYamlDict: should have keys from GrammarYamlKeys
    """
    motif1Generator = getMotifGenerator(aGrammarYamlDict[GrammarYamlKeys.motif1], loadedMotifs, options);
    motif2Generator = getMotifGenerator(aGrammarYamlDict[GrammarYamlKeys.motif2], loadedMotifs, options);

    spacingSetting = aGrammarYamlDict[GrammarYamlKeys.spacingSetting];
    if (spacingSetting == SpacingSettings.fixedSpacing):
        separationGenerator = synthetic.ChooseValueFromASet(aGrammarYamlDict[GrammarYamlKeys_fixedSpacing.fixedSpacingValues]); 
    elif (spacingSetting == SpacingSettings.variableSpacing):
        separationGenerator = synthetic.UniformIntegerGenerator(minVal=aGrammarYamlDict[GrammarYamlKeys_variableSpacing.minimum], maxVal=aGrammarYamlDict[GrammarYamlKeys_variableSpacing.maximum]); 
    else:
        raise RuntimeError("Unsupported value for spacing setting: "+str(spacingSetting)); 
    return synthetic.EmbeddableEmbedder(embeddableGenerator=synthetic.PairEmbeddableGenerator(
                                            substringGenerator1=motif1Generator
                                            ,substringGenerator2=motif2Generator
                                            ,separationGenerator=separationGenerator));

def grammarYamlDictIntegrityCheck(aGrammarYamlDict):
    for key in aGrammarYamlDict:
        if (key not in GrammarYamlKeys.vals and key not in GrammarYamlKeys_fixedSpacing.vals and key not in GrammarYamlKeys_variableSpacing.vals):
            raise RuntimeError("Unrecognised key: "+str(key));

def coinGrammarName(aGrammarYamlDict):
    motif1 = aGrammarYamlDict[GrammarYamlKeys.motif1];
    motif2 = aGrammarYamlDict[GrammarYamlKeys.motif2];
    spacingSetting = aGrammarYamlDict[GrammarYamlKeys.spacingSetting];
    if (spacingSetting == SpacingSettings.fixedSpacing):
        return motif1+"-"+motif2+"-fixedSpacing-"+"-".join(str(x) for x in aGrammarYamlDict[GrammarYamlKeys_fixedSpacing.fixedSpacingValues]);
    elif (spacingSetting == SpacingSettings.variableSpacing):
        return motif1+"-"+motif2+"-variableSpacing-min"+str(aGrammarYamlDict[GrammarYamlKeys_variableSpacing.minimum])+"-max"+str(aGrammarYamlDict[GrammarYamlKeys_variableSpacing.maximum]);
    else:
        raise RuntimeError("Unsupported value for spacing setting: "+str(spacingSetting)); 

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
        embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options); 

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
    embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options);

def embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options):
    embedInBackground = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(options.seqLen) 
        , embedders=[embedder]
    );
    sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, options.numPositiveSeqsPerGrammar)
    synthetic.printSequences(outputFileName, sequenceSet, includeEmbeddings=True);

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

