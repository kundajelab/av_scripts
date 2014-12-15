#!/usr/bin/python
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import re;
import fileProcessing as fp;
import util;

def compileLabelsIntoOneFile(options):  
    #first compile the pattern
    print "compiling pattern",options.labelFromFilenameRegex;
    p = re.compile(options.labelFromFilenameRegex);
    
    entityToLabels = {};
    allLabelsSeen = {}; #a dictionary which I will use as a set
    for inputFile in options.inputFiles:
        print "Processing",inputFile;
        m = p.search(inputFile);
        label = m.group(options.regexGroup); 
        allLabelsSeen[label] = 1;
        def action(inp,lineNumber): #action to perform on each line of file  
            entityId = inp[options.entityIdColumn];
            if entityId not in entityToLabels:
                entityToLabels[entityId] = {};
            entityToLabels[entityId][label] = 1;
        fp.performActionOnEachLineOfFile(
            fp.getFileHandle(inputFile)
            , transformation = util.chainFunctions(fp.trimNewline, fp.splitByTabs)
            , action = action
            , ignoreInputTitle = options.titlePresent 
        );

    outputFileHandle = fp.getFileHandle(options.outputFile,'w');
    sortedLabels = sorted(allLabelsSeen.keys());
    #title:
    outputFileHandle.write("id\t"+"\t".join(sortedLabels));
    for entity in entityToLabels.keys():
        outputFileHandle.write(entity+"\t"+"\t".join(["1" if label in entityToLabels[entity] else "0" for label in sortedLabels]));
    outputFileHandle.close();



if __name__ == "__main__":
    parser = argparse.ArgumentParser("You have a bunch of files, one per label, that tell you the entities which have that label. You want to compile this into a single file with the labels as columns and entities as rows, with 1 if the entity has that label and 0 if not.");
    inputDirDefault = ".";
    parser.add_argument("--inputFiles", nargs="+", help="use glob-like syntax to pass in all the files (organised by label) that detail which entities have a particular label", required=True);
    defaultOutputFile = "multi_label_info.txt";
    parser.add_argument("--outputFile", help="Specify the outputfile, otherwise it will default to "+str(defaultOutputFile), default=defaultOutputFile);
    chromIdColumnDefault = 3;
    parser.add_argument("--entityIdColumn", help="The column index which contains the entity id. Defaults to "+str(chromIdColumnDefault), default=chromIdColumnDefault);    
    labelFromFilenameRegex = "^.*regions_enh_(.*)\\..*$"
    parser.add_argument("--labelFromFilenameRegex", help="How you extract the label from the filename, defaults to "+str(labelFromFilenameRegex)+"; you can specify the regex group containing the label in another param", default=labelFromFilenameRegex);
    defaultRegexGroup = 1; 
    parser.add_argument("--regexGroup", help="If there are multiple regex groups, specify the one that will contain the label; otherwise, this defaults to "+str(defaultRegexGroup), default=defaultRegexGroup);
    parser.add_argument("--titlePresent", help="Set this flag if the files contain a title and you want to skip over the first line", action="store_true");
    compileLabelsIntoOneFile(parser.parse_args());
    


