#!/usr/bin/env python
#for making sure there's an even representation of all the relevant classes.
#read into memory chunks of size '--batchSize'. Then distribute to train/test/validation
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import util;
import fileProcessing as fp;

class SplitOutputFile(object):
    def __init__(self, splitProportion, fileHandle):
        self.splitProportion = splitProportion;
        self.fileHandle = fileHandle;
        self.titlePrinted = False;

def splitIntoTrainingAndValidationSets(options,sep="\t",categoryToLines=None):
    fileHandle = fp.getFileHandle(options.inputFile);
    eof = util.VariableWrapper(False);
   
    splitOutputFiles = [];
    for name,splitProportion in zip(options.splitNames,options.splitProportions):
        #generate the names for the various sets. include the datetime.
        outputPath = fp.getFileNameParts(options.inputFile).getFilePathWithTransformation(lambda x: "split_"+name+"_"+x#+"_"+util.getDateTimeString()
        );
        splitOutputFiles.append(SplitOutputFile(splitProportion, fp.getFileHandle(outputPath,"w")));

    categoryToLines = util.VariableWrapper({}); #I had to wrap it because the 'clear it' line in the action file was otherwise for some reason causing this to be parsed as some local variable...ew.
    #god damn it I need to output a title. Grr.
    title = util.VariableWrapper(None);
    def actionFromTitle(inpTitle):
        title.var = inpTitle;
        def action(inp, lineNumber):
            #I believe lineNumber is 1-indexed so good
            #keep reading into dictionary.
            categoryColumns = [inp[x] for x in options.categoryColumns];
            categoryColumn = "-".join(categoryColumns);
            if categoryColumn not in categoryToLines.var:
                categoryToLines.var[categoryColumn] = [];
            categoryToLines.var[categoryColumn].append(inp);
            if lineNumber%options.batchSize == 0:
                evenlyDistributeLinesToOutputFiles(categoryToLines.var, splitOutputFiles, title.var, sep);
                #clear it
                categoryToLines.var = {};
        return action;
    #perform 'action' on each line of file, with appropriate preprocessing.
    fp.performActionOnEachLineOfFile(fileHandle=fileHandle,actionFromTitle=actionFromTitle,transformation=util.chainFunctions(fp.trimNewline,fp.splitByTabs),ignoreInputTitle=True); 
    #do final stuff to globalish variables left over.
    evenlyDistributeLinesToOutputFiles(categoryToLines.var, splitOutputFiles, title.var, sep);
    for splitOutputFile in splitOutputFiles:
        splitOutputFile.fileHandle.close();
    
def evenlyDistributeLinesToOutputFiles(categoryToLines, splitOutputFiles, title, sep):
    for category in categoryToLines:
        linesForCategory = categoryToLines[category];
        #do an in-place shuffle of linesForCategory
        util.shuffleArray(linesForCategory);
        splitNumbers = util.splitIntegerIntoProportions(len(linesForCategory),[splitOutputFile.splitProportion for splitOutputFile in splitOutputFiles]);
        indexSoFar = 0;
        for splitOutputFile,splitNumber in zip(splitOutputFiles,splitNumbers):
            if (splitOutputFile.titlePrinted == False):
                splitOutputFile.fileHandle.write(title);
                splitOutputFile.titlePrinted = True;
            for line in linesForCategory[indexSoFar : indexSoFar+splitNumber]:
                    splitOutputFile.fileHandle.write(sep.join(line)+"\n");
            indexSoFar += splitNumber;
        assert indexSoFar == len(linesForCategory);

if __name__ == "__main__":
    parser = argparse.ArgumentParser("For splitting up the training, validation and test sets for even class representation");
    categoryColumnDefault = [1];
    parser.add_argument("--categoryColumns", type=int, nargs='+', help="space-sparated list of the columns with the categories to represent evenly; defaults to: "+" ".join([str(x) for x in categoryColumnDefault]), default=categoryColumnDefault);
    batchSizeDefault = 10000;
    parser.add_argument("--batchSize", type=int, default=batchSizeDefault, help="Number of lines to read into memory at a time. Defaults to "+str(batchSizeDefault));
    parser.add_argument("--inputFile", help="The file with the columns to split", required=True);
    splitProportionsDefault = [0.7, 0.15, 0.15];
    parser.add_argument("--splitProportions", nargs='+', type=float, default=splitProportionsDefault, help="Proportions of train/test/validation sets, separated by spaces. Defaults to: "+" ".join([str(x) for x in splitProportionsDefault]));
    splitNamesDefault = ['train', 'valid', 'test'];
    parser.add_argument("--splitNames", nargs='+', default=splitNamesDefault, help="The output files will be three files in the same directory as the input file, with the prefixes based on this argument (output files will be called split_[x]_[inputFileName].txt where [x] is specified here); the default is: "+" ".join(splitNamesDefault));
    args = parser.parse_args();
    if len(args.splitNames) != len(args.splitProportions):
        raise ValueError("Length of splitProportions and splitNames should be equal. Have: "+str(splitProportions)+" and "+str(splitNames));
    print "Note that categoryColumns is set to "+str(args.categoryColumns)+". Setting this incorrectly can lead to odd behaviour.";
    splitIntoTrainingAndValidationSets(args);
