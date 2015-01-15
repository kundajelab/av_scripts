#!/usr/bin/python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;

def extractKey(arr, idxs, makeChromStartEnd):
    subArr = [arr[x] for x in idxs];
    if (makeChromStartEnd):
        assert len(subArr) == 3;
        return util.makeChromStartEnd(subArr[0], subArr[1], subArr[2]);
    else:
        return ";".join(subArr);  

def extractCols(arr, idxs):
    return [arr[x] for x in idxs];

def doTheJoin(options):
    file1_handle = fp.getFileHandle(options.file1);
    file2_handle = fp.getFileHandle(options.file2);
    outputFileHandle = fp.getFileHandle(options.outputFile,'w'); 
    transformationFunc = util.chainFunctions(fp.trimNewline, fp.splitByTabs);
    if (options.presorted):
        def file1Action(file1Line, lineNumber):
            file2Line = transformationFunc(file2_handle.readline());
            file1key = extractKey(file1Line, options.file1KeyIdxs, options.file1_makeChromStartEnd);
            file2key = extractKey(file2Line, options.file2KeyIdxs, options.file2_makeChromStartEnd);
            if (file1key != file2key):
                raise RuntimeError(file1key+" is not "+file2key+" at line "+str(lineNumber));
            toPrint = [];
            toPrint.extend(extractCols(file1Line, options.file1AuxillaryColumns));
            toPrint.extend(extractCols(file2Line, options.file2AuxillaryColumns));
           
            outputFileHandle.write("\t".join(toPrint)+"\n");

        fp.performActionOnEachLineOfFile(
            fileHandle=file1_handle
            , transformation=transformationFunc
            , action = file1Action
            , ignoreInputTitle = False #assuming no input title
            , progressUpdate=options.progressUpdate
        ); 
    else:
        file1dict = {};
        def file1Action(file1Line, lineNumber):
            file1key = extractKey(file1Line, options.file1KeyIdxs, options.file1_makeChromStartEnd);
            file1dict[file1key] = extractCols(file1Line, options.file1AuxillaryColumns);
        print "Reading in file1";
        fp.performActionOnEachLineOfFile(
            fileHandle=file1_handle
            , transformation=transformationFunc
            , action=file1Action
            , ignoreInputTitle=False
            , progressUpdate=options.progressUpdate
        );
        def file2Action(file2Line, lineNumber):
            file2key = extractKey(file2Line, options.file2KeyIdxs, options.file2_makeChromStartEnd);
            toPrint = [];
            toPrint.extend(file1dict[file2key]);
            toPrint.extend(extractCols(file2Line, options.file2AuxillaryColumns));
            outputFileHandle.write("\t".join(toPrint)+"\n");
        print "Performing join with file2";
        fp.performActionOnEachLineOfFile(
            fileHandle = file2_handle
            , transformation = transformationFunc
            , action=file2Action
            , ignoreInputTitle=False
            , progressUpdate=options.progressUpdate
        ) 
    outputFileHandle.close();

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Currently assuming no input title! Also if not presorted, file1 will be read in");
    parser.add_argument("--file1", required=True);
    parser.add_argument("--file2", required=True);
    parser.add_argument("--outputFile", required=True);
    parser.add_argument("--file1KeyIdxs", type=int, nargs='+', required=True);
    parser.add_argument("--file1_makeChromStartEnd", action="store_true");
    parser.add_argument("--file2KeyIdxs", type=int, nargs='+', required=True);
    parser.add_argument("--file2_makeChromStartEnd", action="store_true"); 
    parser.add_argument("--file1AuxillaryColumns", nargs='+', type=int, required=True);
    parser.add_argument("--file2AuxillaryColumns", nargs='+', type=int, required=True);    
    parser.add_argument("--presorted", action="store_true");
    parser.add_argument("--progressUpdate", type=int, default=100000);
    args = parser.parse_args();
    doTheJoin(args);
