#!/usr/bin/env python
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
    if (len(idxs) > 0 and max(idxs) >= len(arr)):
        raise RuntimeError("Indexes has "+str(max(idxs))+" but array has only "+str(len(arr))+" entries: "+str(arr));
    return [arr[x] for x in idxs];

#handles the inversion logic if necessary
def getAuxillaryColumns(selectedColumns, invertIndices, arrayLen):
    return util.invertIndices(selectedColumns, range(arrayLen)) if invertIndices else selectedColumns;

def getOutputFilePath(file1,prefix):
    return fp.getFileNameParts(file1).getFilePathWithTransformation(lambda x: prefix+x)

def doTheJoin(options):
    file2_handle = fp.getFileHandle(options.file2);
    transformationFunc = util.chainFunctions(fp.trimNewline, fp.splitByTabs);
    if (options.presorted):
        file1_handle = fp.getFileHandle(options.file1);
        outputFileHandle = fp.getFileHandle(options.outputFile if options.outputFile is not None else getOutputFilePath(options.file1, options.outputFilePrefix_file2[0]),'w'); 
        def file1Action(file1Line, lineNumber):
            file2Line = transformationFunc(file2_handle.readline());
            file1key = extractKey(file1Line, options.file1KeyIdxs, options.file1_makeChromStartEnd);
            file2key = extractKey(file2Line, options.file2KeyIdxs, options.file2_makeChromStartEnd);
            if (file1key != file2key):
                raise RuntimeError(file1key+" is not "+file2key+" at line "+str(lineNumber));
            toPrint = [];
            file1AuxillaryCols = getAuxillaryColumns(options.file1SelectedColumns, options.file1_invertColumnSelection, len(file1Line))
            file2AuxillaryCols = getAuxillaryColumns(options.file2SelectedColumns, options.file2_invertColumnSelection, len(file2Line))
            toPrint.extend(extractCols(file1Line, file1AuxillaryCols));
            toPrint.extend(extractCols(file2Line, file2AuxillaryCols));
           
            outputFileHandle.write("\t".join(toPrint)+"\n");

        fp.performActionOnEachLineOfFile(
            fileHandle=file1_handle
            , transformation=transformationFunc
            , action = file1Action
            , ignoreInputTitle = options.titlePresent
            , progressUpdate=options.progressUpdate
        ); 
        outputFileHandle.close();
    else: #if not presorted
        file1dicts = [];
        filetitle = [];
        outputFileHandles = [];
        missingKeysTrackers = [];
        for (i, file1) in enumerate(options.file1):
            print "Slurping",file1;
            file1dict = {};
            file1dicts.append(file1dict);
            missingKeysTrackers.append(util.VariableWrapper(0));
            if (options.outputFilePrefix_file2 is not None):
                theFileName = getOutputFilePath(options.file2, options.outputFilePrefix_file2[i]);
            else:
                theFileName = options.outputFile if options.outputFile is not None else getOutputFilePath(file1, options.outputFilePrefix_file1);
            outputFileHandles.append(fp.getFileHandle(theFileName,'w'));
            def file1Action(file1Line, lineNumber):
                extractedCols = extractCols(file1Line, getAuxillaryColumns(options.file1SelectedColumns, options.file1_invertColumnSelection, len(file1Line)));
                file1key = extractKey(file1Line, options.file1KeyIdxs, options.file1_makeChromStartEnd);
                if (lineNumber == 1 and options.titlePresent):
                    if len(filetitle)==0:
                        filetitle.extend(extractedCols);
                else:
                    file1dict[file1key] = extractedCols
            fp.performActionOnEachLineOfFile(
                fileHandle=fp.getFileHandle(file1)
                , transformation=transformationFunc
                , action=file1Action
                , ignoreInputTitle=False #incorporate the title using the logic in action
                , progressUpdate=options.progressUpdate
            );
        def file2Action(file2Line, lineNumber):
            extractedCols = extractCols(file2Line, getAuxillaryColumns(options.file2SelectedColumns,options.file2_invertColumnSelection, len(file2Line)));
            if (lineNumber == 1 and options.titlePresent):
                filetitle.extend(extractedCols);
                for outputFileHandle in outputFileHandles:
                    outputFileHandle.write("\t".join(filetitle)+"\n");
            else: 
                file2key = extractKey(file2Line, options.file2KeyIdxs, options.file2_makeChromStartEnd);
                for file1dict,outputFileHandle,missingKeys in zip(file1dicts,outputFileHandles,missingKeysTrackers): 
                    if file2key not in file1dict:
                        missingKeys.var += 1;
                    else:
                        toPrint = [];
                        toPrint.extend(file1dict[file2key]);
                        toPrint.extend(extractedCols);
                        outputFileHandle.write("\t".join(toPrint)+"\n");
        print "Performing join with file2";
        fp.performActionOnEachLineOfFile(
            fileHandle = file2_handle
            , transformation = transformationFunc
            , action=file2Action
            , ignoreInputTitle=False #handle the title using the logic in action
            , progressUpdate=options.progressUpdate
        );
        for file1,missingKeys in zip(options.file1,missingKeysTrackers):
            print "Missed "+str(missingKeys.var)+" keys for",file1;
        for fileHandle in outputFileHandles:
            fileHandle.close();

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Please indicate if title present! Also if not presorted, file1s will be read in. Specifying multiple file 1's results in multiple joins in one go (output file prefix should be specified); there will be one output file per join.");
    parser.add_argument("--file1", nargs='+', required=True);
    parser.add_argument("--file2", required=True);
    parser.add_argument("--outputFile", help="Either specify an output file name, or specify one of the --outputFilePrefix (which will go in front of either the file1 or the file2 name)");
    parser.add_argument("--outputFilePrefix_file1", help="Either one of these or otuputFile should be specified. If this is specified, the prefix will go in front of each file1 name");
    parser.add_argument("--outputFilePrefix_file2", nargs='+', help="Either one of these or outputFile should be specified. If this is specified, you need one prefix per file1 name; prefix applied to file2 name");
    parser.add_argument("--file1KeyIdxs", type=int, nargs='+', required=True);
    parser.add_argument("--file1_makeChromStartEnd", action="store_true");
    parser.add_argument("--file2KeyIdxs", type=int, nargs='+', required=True);
    parser.add_argument("--file2_makeChromStartEnd", action="store_true"); 
    parser.add_argument("--file1SelectedColumns", nargs='*', type=int, required=True);
    parser.add_argument("--file1_invertColumnSelection", action="store_true", help="If selected, all columns EXCEPT these will be included");
    parser.add_argument("--file2SelectedColumns", nargs='*', type=int, required=True);   
    parser.add_argument("--file2_invertColumnSelection", action="store_true", help="If selected, all columns EXCEPT these will be included"); 
    parser.add_argument("--presorted", action="store_true");
    parser.add_argument("--titlePresent", action="store_true");
    parser.add_argument("--progressUpdate", type=int, default=100000);
    args = parser.parse_args();
    mutexOpt = ['outputFile', 'outputFilePrefix_file1', 'outputFilePrefix_file2'];
    if (sum([util.presentAndNotNone(args,x) for x in mutexOpt]) != 1):
        print "Please specify exactly one of "+str(mutexOpt);
        sys.exit(1);
    if (len(args.file1) > 1):
        if (args.outputFilePrefix_file2 is None and args.outputFilePrefix_file1 is None):
            print "If multiple file 1's are present, either outputFilePrefix_file2 or outputFilePrefix_file1 should be specified";
            sys.exit(1);
        if (args.outputFilePrefix_file2 is not None and len(args.outputFilePrefix_file2) != len(args.file1)):
            print "Length of outputFilePrefix_file2 should match length of file1; is "+str(len(args.outputFilePrefix_file2))+" and "+str(len(args.file1));
        if (args.presorted):
            print "The idea of specifying multiple file 1's is that the join would be done in one pass through file2 by reading all the file1's into memory. The point of the --presorted flag is to not read everything into memory. Therefore, if you want to do joins with multiple file1's but don't want to read everything into memory, you should call this join script once per file. It is BEST if you do this sequentially and not in parallel because if you do it in parallel you will incur a lot of overhead from the read head jumping between files";
            sys.exit(1);
    doTheJoin(args);
