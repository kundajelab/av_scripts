#!/usr/bin/env python
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter
import util;
from synthetic import synthetic;

def simulate(options):
    outputFileName = util.addArguments("variableSpacingSimulation", [
                            util.ArgumentToAdd(options.seqLengthMin, "seqLengthMin")
                            , util.ArgumentToAdd(options.seqLengthMax, "seqLengthMax")
                            , util.ArgumentToAdd(options.numSeq, "numSeq")
                            , util.BooleanArgument(options.labelPos, "labelPos")
                            , util.ArgumentToAdd(options.minSep, "minSep")
                            , util.ArgumentToAdd(options.maxSep, "maxSep")
                            ] )+".simdata";

    labelsFromGeneratedSequenceFunction = lambda self, x: ["1"] if options.labelPos else ["0"];
    labelGenerator = synthetic.LabelGenerator(["Label"], labelsFromGeneratedSequenceFunction ); 
    
    substringGenerator=synthetic.FixedSubstringGenerator("1")
    embedders = [];
    embedders.append(synthetic.EmbeddableEmbedder(
                        embeddableGenerator=synthetic.PairEmbeddableGenerator(
                            substringGenerator1=substringGenerator
                            ,substringGenerator2=substringGenerator
                            ,separationGenerator=synthetic.UniformIntegerGenerator(minVal=options.minSep
                                                        ,maxVal=options.maxSep)
                        )
                    ));

    embedInBackground = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.RepeatedSubstringBackgroundGenerator(
                substringGenerator=synthetic.FixedSubstringGenerator("0")
                , repetitions=synthetic.UniformIntegerGenerator(options.seqLengthMin, options.seqLengthMax)) 
        , embedders=embedders
        , namePrefix="synth"+("Pos" if options.labelPos else "Neg")
    );

    sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, options.numSeq)
    synthetic.printSequences(outputFileName, sequenceSet, labelGenerator=labelGenerator);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--seqLengthMin", type=int, required=True)
    parser.add_argument("--seqLengthMax", type=int, required=True)
    parser.add_argument("--numSeq", type=int, required=True);
    parser.add_argument("--labelPos", action="store_true");
    parser.add_argument("--minSep", type=int, required=True);
    parser.add_argument("--maxSep", type=int, required=True);
    options = parser.parse_args();
    simulate(options);

