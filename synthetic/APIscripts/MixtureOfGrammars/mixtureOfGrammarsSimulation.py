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

def getMotifGenerator(motifName, loadedMotifs, options):
    kwargs={'loadedMotifs':loadedMotifs}
    if (options.bestHitForMotifs):
        theClass=synthetic.BestHitPwmFromLoadedMotifs;
        kwargs['bestHitMode']=bestHitMode=pwm.BEST_HIT_MODE.pwmProb; #prob don't need to twiddle this
    else:
        theClass=synthetic.PwmSamplerFromLoadedMotifs;
        
    motif1Generator=theClass(motifName=motifName1,**kwargs)

def getEmbedderFromGrammarYaml(aGrammarYamlObject, loadedMotifs, options):
    """
        aGrammarYamlObject: should have keys from GrammarYamlKeys
    """
    motif1Generator = getMotifGenerator(aGrammarYamlObject[GrammarYamlKeys.motif1], loadedMotifs, options);
    motif2Generator = getMotifGenerator(aGrammarYamlObject[GrammarYamlKeys.motif2], loadedMotifs, options);

    spacingSetting = aGrammarYamlObject[GrammarYamlKeys.spacingSetting];
    if (spacingSetting == SpacingSettings.fixedSpacing):
        separationGenerator = synthetic.ChooseValueFromASet(aGrammarYamlObject[GrammarYamlKeys_fixedSpacing.fixedSpacingValues]); 
    elif (spacingSetting == SpacingSettings.variableSpacing):
        separationGenerator = synthetic.UniformIntegerGenerator(minVal=aGrammarYamlObject[GrammarYamlKeys_variableSpacing.minimum], maxVal=aGrammarYamlObject[GrammarYamlKeys_variableSpacing.maximum]); 
    else:
        raise RuntimeError("Unsupported value for spacing setting: "+str(spacingSetting)); 
    return synthetic.EmbeddableEmbedder(embeddableGenerator=synthetic.PairEmbeddableGenerator(
                                            substringGenerator1=motif1Generator
                                            ,substringGenerator2=motif2Generator
                                            ,separationGenerator=separationGenerator));

def grammarYamlObjectIntegrityCheck(aGrammarYamlObject):
    for key in aGrammarYamlObject:
        if (key not in GrammarYamlKeys.vals and key not in GrammarYamlKeys_fixedSpacing.vals and key not in GrammarYamlKeys_variableSpacing.vals):
            raise RuntimeError("Unrecognised key: "+str(key));

def coinGrammarName(aGrammarYamlObject):
    motif1 = aGrammarYamlObject[GrammarYamlKeys.motif1];
    motif2 = aGrammarYamlObject[GrammarYamlKeys.motif2];
    spacingSetting = aGrammarYamlObject[GrammarYamlKeys.spacingSetting];
    if (spacingSetting == SpacingSettings.fixedSpacing):
        return motif1+"-"+motif2+"-fixedSpacing-"+"-".join(aGrammarYamlObject[GrammarYamlKeys_fixedSpacing.fixedSpacingValues]);
    elif (spacingSetting == SpacingSettings.variableSpacing):
        return motif1+"-"+motif2+"-variableSpacing-min"+str(aGrammarYamlObject[GrammarYamlKeys_variableSpacing.minimum])+"-max"+str(aGrammarYamlObject[GrammarYamlKeys_variableSpacing.maximum]);
    else:
        raise RuntimeError("Unsupported value for spacing setting: "+str(spacingSetting)); 

def generatePositives(options, grammarsYaml, loadedMotifs):
    print("Generating positives");
    for aGrammarYamlObject in grammarsYaml:
        if hasattr(aGrammarYamlObject, GrammarYamlKeys.grammarName):
            grammarName = aGrammarYamlObject[GrammarYamlKeys.grammarName];
        else:
            grammarName = coinGrammarName(aGrammarYamlObject);
        print("Generating "+grammarName);
        argumentsToAdd = [util.ArgumentToAdd(grammarName, "grammar"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numPositiveSeqsPerGrammar, "numSeq")];
        outputFileName = util.addArguments("positiveSet",argumentsToAdd)+".simdata";
        embedder = getEmbedderFromGrammarYaml(aGrammarYamlObject);  
        embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options); 

def generateNegatives(options, grammarsYaml, loadedMotifs):
    print("Generating negatives");
    if options.numNegativeSeqs is None:
        options.numNegativeSeqs = options.numPositiveSeqsPerGrammar*len(grammarsYaml);
    from collections import OrderedDict;
    appearingMotifsDict = OrderedDict();
    #compile the set of motifs that appear
    for aGrammarYamlObject in grammarsYaml:
        for key in [GrammarYamlKeys.motif1, GrammarYamlKeys.motif2]:
        appearingMotifsDict[aGrammarYamlObject[key]] = 1;
    appearingMotifs = appearingMotifsDict.keys();
    print("Appearing motifs: "+", ".join(appearingMotifs));
    motifEmbedders = [sythetic.EmbeddableEmbedder(embeddableGenerator=getMotifGenerator(motifName, loadedMotifs, options)) for motifName in appearingMotifs];
    quanityGenerator = synthetic.MinMaxWrapper(synthetic.PoissonQuantityGenerator(options.meanMotifsInNegative), theMax=options.maxMotifsInNegative);
    embedder = synthetic.RandomSubsetOfEmbedders(quanityGenerator=quanityGenerator, embedders=motifEmbedders);  
    argumentsToAdd = [util.CoreFileNameArgument(options.grammarsYaml, "grammarsYaml"), util.ArgumentToAdd(options.seqLen, "seqLen"), util.ArgumentToAdd(options.numNegativeSeqs, "numSeq"), util.ArgumentToAdd(options.meanMotifsInNegative, "meanMotifs"), util.ArgumentToAdd(options.maxMotifsInNegative, "maxMotifs")];
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
    generatePositives(options, grammarsYaml, loadedMotifs);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--pathToMotifs", required=True, help="Path to the file with the pwms");
    parser.add_argument("--grammarsYaml", required=True, help="A yaml file containing all the grammars");
    parser.add_argument("--seqLen", required=True, type=int);
    parser.add_argument("--numPositiveSeqsPerGrammar", type=int, required=True);
    parser.add_argument("--numNegativeSeqs", type=int, help="If not specified, will default to equal total size of positive set");
    parser.add_argument("--meanMotifsInNegative", type=int, default=2, help="Defaults to 2; poission sampled");
    parser.add_argument("--maxMotifsInNegative", type=int, default=4, help="Defaults to 4");
    options = parser.parse_args();
    doMixtureOfGrammarsSimulation(options); 

