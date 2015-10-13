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
    outputFileName = util.addArguments("positionalGrammarSimulation", [
                            util.ArgumentToAdd(options.seqLength, "seqLength")
                            , util.ArgumentToAdd(options.numSeq, "numSeq")
                            , util.BooleanArgument(options.outsideCentralBp, "outsideCentralBp")
                            , util.ArgumentToAdd(options.centralBp, "centralBp")
                            ] )+".simdata";

    labelsFromGeneratedSequenceFunction = lambda self, x: ["0"] if options.outsideCentralBp else ["1"];
    labelGenerator = synthetic.LabelGenerator(["Label"], labelsFromGeneratedSequenceFunction ); 
    
    substringGenerator=synthetic.FixedSubstringGenerator("1")
    embedders = [];
    embedders.append(synthetic.EmbeddableEmbedder(
                        embeddableGenerator=synthetic.SubstringEmbeddableGenerator(
                            substringGenerator=substringGenerator
                        )
                        ,positionGenerator=(synthetic.OutsideCentralBp(options.centralBp) if options.outsideCentralBp else synthetic.InsideCentralBp(options.centralBp))
                    ));

    embedInBackground = synthetic.EmbedInABackground(
        backgroundGenerator=synthetic.RepeatedSubstringBackgroundGenerator(substringGenerator=synthetic.FixedSubstringGenerator("0"), repetitions=options.seqLength) 
        , embedders=embedders
        , namePrefix="synth"+("Neg" if options.outsideCentralBp else "Pos")
    );

    sequenceSet = synthetic.GenerateSequenceNTimes(embedInBackground, options.numSeq)
    synthetic.printSequences(outputFileName, sequenceSet, labelGenerator=labelGenerator);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--seqLength", type=int, required=True)
    parser.add_argument("--numSeq", type=int, required=True);
    parser.add_argument("--outsideCentralBp", action="store_true");
    parser.add_argument("--centralBp", type=int, required=True);
    options = parser.parse_args();
    simulate(options);
