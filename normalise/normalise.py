#!/usr/bin/python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import argparse;

NORMALISATION_MODE = util.enum(meanVariance = "meanVariance");

NORMALISATION_STATS_NAME = util.enum(Mean = "Mean", StandardDeviation = "StandardDeviation", featureName="featureName");

class StatsForFeature(object):
    def __init__(self, featureName):
        self.featureName = featureName;

def getFeatureToInfoMap(options):
    transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs);
    featureToInfoMap = {};
    def actionFromTitle(title):
        titleArr = transformation(title);
        colNameToIdxMap = util.valToIndexMap(titleArr);
        def action(inp, lineNumber):
            featureName = inp[colNameToIdxMap[NORMALISATION_STATS_NAME.featureName]];
            statsForFeature = StatsForFeature(featureName);
            featureToInfoMap[featureName] = statsForFeature; 
            if (options.normalisationMode == NORMALISATION_MODE.meanVariance):
                statsForFeature.mean = inp[colNameToIdxMap[NORMALISATION_STATS_NAME.Mean]];
                statsForFeature.sdev = inp[colNameToIdxMap[NORMALISATION_STATS_NAME.StandardDeviation]];
            else:
                raise RuntimeError("unsupported normalisation mode: "+str(options.normalisationMode));
        return action;
    fp.performActionOnEachLineOfFile(
        fileHandle = fp.getFileHandle(options.statsToNormaliseWith)
        , transformation=transformation
        , actionFromTitle = actionFromTitle
        , ignoreInputTitle = True #title present
    );
    return featureToInfoMap;

def normaliseVal(val, info, options):
    if (options.normalisationMode == NORMALISATION_MODE.meanVariance):
        return float(val - info.mean)/info.sdev;
    else:
        raise RuntimeError("unsupported normalisation mode: "+str(options.normalisationMode));

def normalise(options):
    featureToInfoMap = getFeatureToInfoMap(options);
    transformation = util.defaultTransformation(); 
    outputFile = fp.getFileNameParts(options.fileToNormalise).getFilePathWithTransformation(
                        lambda x: "normalised_"+options.normalisationMode+"_"+fp.getCoreFileName(options.statsToNormaliseWith));
    outputFileHandle = fp.getFileHandle(outputFile, 'w');
    def actionFromTitle(title): 
        titleArr = transformation(title);
        outputFileHandle.write(title);
        def action(inp, lineNumber):
            toPrint = [];
            for (i,val) in enumerate(inp):
                colName = titleArr[i];
                if colName not in feaureToInfoMap:
                    toPrint.append(val);
                else:
                    toPrint.append(str(normaliseVal(float(val))));
            outputFileHandle.write("\t".toPrint+"\n"); 
    fp.performActionOnEachLineOfFile(
        fileHandle=fp.getFileHandle(options.fileToNormalise)
        , transformation=transformation
        , actionFromTitle=actionFromTitle
        , ignoreInputTitle=True #title present
    );
    outputFileHandle.close();

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--fileToNormalise", required=True);
    parser.add_argument("--statsToNormaliseWith", required=True);
    parser.add_argument("--normalisationMode", choices=NORMALISATION_MODE.vals, default=NORMALISATION_MODE.meanVariance);
    
    args = parser.parse_args();
    normalise(args);
