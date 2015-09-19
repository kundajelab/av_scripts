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
                            ] );
    
    substringGenerator=synthetic.FixedSubstringGenerator("1")
    embedders = [];
    embedders.append(synthetic.EmbeddableEmbedder(
                        embeddableGenerator=synthetic.SubstringEmbeddableGenerator(
                            substringGenerator=substringGenerator
                        )
                        ,positionGenerator=(synthetic.OutsideCentralBp(options.centralBp) if options.outsideCentralBp else synthetic.InsideCentralBp(options.centralBp))
                    ));

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
    parser.add_argument("--outsideCentralBp", action="store_true");
    parser.add_argument("--centralBp", type=int, required=True);
    options = parser.parse_args();
    simulate(options);
