#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import bedtoolsExtension.bedToFasta as bedToFasta;
import fileProcessing as fp;
import util;
import argparse;

def bedToFastaForAllBedInDirectory(inputDir, finalOutputFile, faSequencesDir):
    inputBedFiles = glob.glob(inputDir+"/*");
    tempDir = util.getTempDir();
    outputFileFromInputFile = lambda inputFile: tempDir + "/" + "fastaExtracted_" + fp.getFileNameParts(inputFile).coreFileName + ".tsv";
    util.executeForAllFilesInDirectory(inputDir, 
        lambda anInput : bedToFasta_function.bedToFasta(anInput, outputFileFromInputFile(anInput), faSequencesDir));

    #concatenate files using cat
    fp.concatenateFiles_preprocess(
        finalOutputFile
        , [outputFileFromInputFile(inputBedFile) for inputBedFile in inputBedFiles]
        , transformation=lambda line,filename: filename+"\t"+line
        , outputTitleFromInputTitle = lambda x : "sourceBed\tchromosomeLocation\tsequence\n");

#executes bedToFasta on all bed files in a directory
if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputDir", required=True);
    parser.add_argument("--outputFile");
    parser.add_argument("--faSequencesDir", required=True);
    args = parser.parse_args();
    if (args.outputFile is None):
        args.outputFile = fp.getFileNameParts(args.inputBedFile).getFilePathWithTransformation(lambda x: "fastaExtracted_"+x, extension=".tsv")

    inputBedFile = args.inputBedFile;
    finalOutputFile = args.outputFile;
    faSequencesDir = args.faSequencesDir;
    bedToFasta_allBedInDir_function.bedToFastaForAllBedInDirectory(inputDir, finalOutputFile, sequencesDir);

