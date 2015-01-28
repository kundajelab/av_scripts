#!/srv/gs1/software/python/python-2.7/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;
from profileSequences import getLetterByLetterKeysGenerator, gcLetterToKey, GCkeys;

#iterator that maps acgtn/ACGTN in sequence to 'keys' relevant for computing GC content
gcKeysGenerator = getLetterByLetterKeysGenerator(gcLetterToKey);
def getGCcontent(sequence):
    numGC = 0;
    numSeq = 0; #excluding Ns
    for gcKey in gcKeysGenerator:
        if (gcKey != GCkeys.N):
            numSeq += 1;
            if (gcKey == GCkeys.GC):
                numGC += 1;
    return (0 if numSeq == 0 else float(numGC)/float(numSeq)); 

def perSequence_profile(options):   
    transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs);
    prefix = util.addArguments("profiled", [util.BooleanArgument(options.gcContent, "gcContent")
                                            ,util.ArgumentToAdd(options.sequencesLength, "seqLen")]);  
    outputFile = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: prefix+x);
    outputFileHandle = fp.getFileHandle(outputFile, 'w');
    def actionFromTitle(title):
        titleArr = transformation(title);
        if (options.titlePresent):
            toPrintTitleArr = [titleArr[x] for x in options.auxillaryCols];
        else:
            toPrintTitleArr = [x for x in options.auxillaryColNames]; 
        if (options.gcContent):
            toPrintTitleArr.append("gcContent");
        outputFileHandle.write("\t".join(toPrintTitleArr)+"\n"); 
        def action(inp, lineNumber):
            toPrintArr = [inp[x] for x in options.auxillaryCols];
            sequence = inp[options.sequenceCol];
            if (options.gcContent):
                toPrintArr.extend(getGCcontent(sequence));
            outputFileHandle.write("\t".join(toPrintArr)+"\n"); 
        if (options.titlePresent == False):
            action(titleArr, 0); #if there's no title, perform the action on the first line
        return action;
    fp.performActionOnEachLineOfFile(
        fileHandle = fp.getFileHandle(options.inputFile)
        , transformation=transformation
        , actionFromTitle = actionFromTitle
        , ignoreInputTitle = options.titlePresent
    );
    outputFileHandle.close();
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--inputFile", required=True);
    parser.add_argument("--gcContent", action="store_true");
    parser.add_argument("--sequenceCol", default=1);
    parser.add_argument("--sequencesLength", type=int, required=True);
    parser.add_argument("--auxillaryCols", nargs='+', default=[0]);
    parser.add_argument("--auxillaryColNames", nargs='+', default=['id']);
    parser.add_argument("--titlePresent", action="store_true");
    args = parser.parse_args();

    if (args.titlePresent == False):
        if (len(args.auxillaryCols) > 0):
            if (args.auxillaryColNames is None):
                raise ValueError("If no title present, need to specify the names associated with the auxillary cols");
            if (len(args.auxillaryColNames) != len(args.auxillaryCols)):
                raise ValueError("Num of auxillary col names should be same as num of auxillary cols");

    perSequence_profile(args);
