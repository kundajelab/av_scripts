#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--matrixFile", required=True);
    parser.add_argument("--numberOfPcsToTruncateTo", type=int, required=True);
    options = parser.parse_args();

    pcaOutputFile = fp.getFileNameParts(options.matrixFile).getFilePathWithTransformation(lambda x: "pca_"+x, extension=".txt");
    util.executeAsSystemCall("doPCA.R "+options.matrixFile+" "+pcaOutputFile);
    util.executeAsSystemCall("perl -i -pe '$_ = $. == 1 ? \"\\t$_\" : $_' "+pcaOutputFile);
    trucatedPcaOutputFile = fp.getFileNameParts(pcaOutputFile).getFilePathWithTransformation(lambda x: "top"+str(options.numberOfPcsToTruncateTo)+"Components_"+x);
    util.executeAsSystemCall("perl -pe '@_ = split(/\\t/, $_); $\" = \"\\t\"; $_ = \"@_[0.."+str(options.numberOfPcsToTruncateTo)+"]\\n\"' "+pcaOutputFile+" > "+trucatedPcaOutputFile);
