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
import pathSetter
from synthetic import synthetic;
import util;
from pwm import pwm;
from apiHelperFunctions import getMotifGenerator;  

GrammarYamlKeys = util.enum(motif1="motif1",motif2="motif2",spacingSetting="spacingSetting",grammarName="grammarName");
SpacingSettings = util.enum(fixedSpacing="fixedSpacing", variableSpacing="variableSpacing");
GrammarYamlKeys_fixedSpacing = util.enum(fixedSpacingValues="fixedSpacingValues"); #keys applicable to the case of fixedSpacing
GrammarYamlKeys_variableSpacing = util.enum(minimum="minimum", maximum="maximum"); #keys applicable to the case of variable spacing

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

def grammarYamlDictIntegrityCheck(aGrammarYamlDict):
    for key in aGrammarYamlDict:
        if (key not in GrammarYamlKeys.vals and key not in GrammarYamlKeys_fixedSpacing.vals and key not in GrammarYamlKeys_variableSpacing.vals):
            raise RuntimeError("Unrecognised key: "+str(key));

def getEmbedderFromGrammarYaml(aGrammarYamlDict, loadedMotifs, options, grammarName=None):
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
                                            ,separationGenerator=separationGenerator)
                                            , name=grammarName);

def embedInABackgroundAndGenerateSeqs(embedder, outputFileName, options, numberOfSequences, includeEmbeddings=True, labelGenerator=None):
    embedInBackground = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.ZeroOrderBackgroundGenerator(options.seqLen) 
        , embedders=[embedder]
    );
    sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, numberOfSequences)
    synthetic.printSequences(outputFileName, sequenceSet, includeEmbeddings=includeEmbeddings, labelGenerator=labelGenerator);
