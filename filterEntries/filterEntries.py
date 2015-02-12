#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;

def filterEntries(options):
   
    idsToIncludeDict = {}; 
    idsToExcludeDict = {};
    inclusionActive = False;
    exclusionActive = False;
    if (len(options.filesWithLinesToInclude) > 0):
        inclusionActive = True;
        readIdsIntoDict(options.filesWithLinesToInclude, idsToIncludeDict, options.filesWithLinesToInclude_cols, options.titlePresentFilterFiles);
    if (len(options.filesWithLinesToExclude) > 0):
        exclusionActive = True;
        readIdsIntoDict(options.filesWithLinesToExclude, idsToExcludeDict, options.filesWithLinesToExclude_cols, options.titlePresentFilterFiles);
    assert (inclusionActive or exclusionActive);    

    for fileWithLinesToFilter in options.filesWithLinesToFilter:
        fileNameParts = fp.getFileNameParts(fileWithLinesToFilter); 
        outputDir = options.outputDir
        if outputDir is None:
           outputDir = fileNameParts.directory;  
        outputFileName = outputDir+"/"+fileNameParts.getFileNameWithTransformation(lambda x: options.outputPrefix+x);
        outputFileHandle = fp.getFileHandle(outputFileName, 'w');
        
        print "Filtering",fileWithLinesToFilter;
        def action(inpArr,lineNumber):
            theId = extractId(inpArr, options.filesWithLinesToFilter_cols);
            passes = False;
            include = theId in idsToIncludeDict;
            exclude = theId in idsToExcludeDict;
            if (exclusionActive==False):
                assert inclusionActive == True;
                passes = include;
            elif (inclusionActive==False):
                assert exclusionActive == True;
                passes = (exclude == False);
            else:
                assert inclusionActive and exclusionActive;
                if (excludeHasPrecedence):
                    passes = False if exclude else include; #include if on the inclusion list UNLESS appears on the exclusion list.
                else:
                    passes = True if include else (exclude==False); #exclude if on the exclusion list UNLESS appears on the inclusion list.
            if passes:
                outputFileHandle.write("\t".join(inpArr)+"\n");
        
        fileHandle = fp.getFileHandle(fileWithLinesToFilter)
        if (options.titlePresentOrig):
            outputFileHandle.write(fileHandle.readline());
        fp.performActionOnEachLineOfFile(
            fileHandle
            , transformation=util.chainFunctions(fp.trimNewline,fp.splitByTabs)
            ,action=action
        );

def readIdsIntoDict(files, theDict, idCols, titlePresent):
    for aFile in files:
        fileHandle = fp.getFileHandle(aFile);
        def action(inpArr, lineNumber):
            theId = extractId(inpArr,idCols);
            theDict[theId] = 1;
        fp.performActionOnEachLineOfFile(
            fileHandle
            , transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs)
            , action = action
            , ignoreInputTitle = titlePresent
        );

def extractId(inpArr, idCols):
    return "_".join([inpArr[x] for x in idCols]);

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Filters some files according to other files, given that each file has a unique set of 'index' columns. Remember to set a flag if the title is present. By default, assumes column to filter accoridng to is the first one. Also assumes TSVs (tab separated files)");
    parser.add_argument('--titlePresentOrig', help="title is present on original file", action="store_true");
    parser.add_argument('--titlePresentFilterFiles', help="title is present on files that contain lines to include/exclude", action="store_true");
    parser.add_argument('--filesWithLinesToFilter', nargs='+', required=True);
    parser.add_argument('--filesWithLinesToInclude', nargs='+', default=[]);
    parser.add_argument('--filesWithLinesToExclude', nargs='+', default=[]);
    parser.add_argument('--filesWithLinesToFilter_cols', nargs='+', help="Column indexes forming unique identifier in the files to filter", type=int, default=[0]);
    parser.add_argument('--filesWithLinesToInclude_cols', nargs='+', type=int, default=[0]);
    parser.add_argument('--filesWithLinesToExclude_cols', nargs='+', type=int, default=[0]);
    parser.add_argument('--excludeHasPrecedence', help="Include this flag to make exclusion take precedence over inclusion, for when a line appears in both", action="store_true");
    parser.add_argument('--outputPrefix', default='filtered_');
    parser.add_argument('--outputDir',help="Will default to the same directory that the input file to be filtered lives in");

    args = parser.parse_args();
    
    if (len(args.filesWithLinesToInclude) and len(args.filesWithLinesToExclude)):
        print "At least one of filesWithLinesToInclude or filesWithLinesToExclude should be provided";
        sys.exit(1);
    
    filterEntries(parser.parse_args());
