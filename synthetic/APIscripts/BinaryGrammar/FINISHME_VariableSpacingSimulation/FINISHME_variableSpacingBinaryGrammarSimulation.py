#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
from synthetic import synthetic;
import simulationParams_binaryGrammarSimulation;
from simulationParams_binaryGrammarSimulation import generationSettings;

seqLength = simulationParams_binaryGrammarSimulation.seqLength;
numSeq = simulationParams_binaryGrammarSimulation.numSeq;
generationSetting = simulationParams_binaryGrammarSimulation.generationSetting;
def simulat(options):
    outputFileName = "binaryGrammarSimulation_"+generationSetting+"_seqLength"+str(seqLength)+"_numSeq"+str(numSeq)+".simdata";

    substringGenerator=synthetic.FixedSubstringGenerator("1")
    uniform1embedder=synthetic.SubstringEmbedder(substringGenerator=substringGenerator)

    embedders = [];
    if (generationSetting == generationSettings.allZeros):
        pass;
    elif (generationSetting in [generationSettings.single1, generationSettings.twoOnes]):
        embedders.append(uniform1embedder);
        if (generationSetting in [generationSettings.twoOnes]):
            embedders.append(uniform1embedder);
    elif (generationSetting in [generationSettings.twoOnesFixedSpacing, generationSettings.twoOnesVariableSpacing]):
        if (generationSetting==generationSettings.twoOnesFixedSpacing):
            separationGenerator=synthetic.FixedQuantityGenerator(simulationParams_binaryGrammarSimulation.fixedSpacingOrMinSpacing);
        elif (generationSetting==generationSettings.twoOnesVariableSpacing):
            separationGenerator=synthetic.UniformIntegerGenerator(minVal=simulationParams_binaryGrammarSimulation.fixedSpacingOrMinSpacing
                                                                    ,maxVal=simulationParams_binaryGrammarSimulation.maxSpacing);
        else:
            raise RuntimeError("unsupported generationSetting:"+generationSetting);
        embedders.append(synthetic.EmbeddableEmbedder(
                            embeddableGenerator=synthetic.PairEmbeddableGenerator(
                                substringGenerator1=substringGenerator
                                ,substringGenerator2=substringGenerator
                                ,separationGenerator=separationGenerator
                            )
                        ));
    else:
        raise RuntimeError("unsupported generationSetting:"+generationSetting);
        

    embedInBackground = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.RepeatedSubstringBackgroundGenerator(substringGenerator=synthetic.FixedSubstringGenerator("0"), repetitions=seqLength) 
        , embedders=embedders
    );

    sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, numSeq)
    synthetic.printSequences(outputFileName, sequenceSet);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--seqLength", type=int, required=True)
    parser.add_argument("--numSeq", type=int, required=True);
    parser.add_argument("--minSpacing", type=int, required=True);
    parser.add_argument("--maxSpacing", type=int, required=True); 
