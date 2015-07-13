import sys;
import re;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import gzip;

def getCoreFileName(fileName):
    return getFileNameParts(fileName).coreFileName;

def getFileNameParts(fileName):
    p = re.compile(r"^(.*/)?([^\./]+)(\.[^/]*)?$");
    m = p.search(fileName);
    return FileNameParts(m.group(1), m.group(2), m.group(3));

class FileNameParts:
    def __init__(self, directory, coreFileName, extension):
        self.directory = directory if (directory is not None) else os.getcwd();
        self.coreFileName = coreFileName;
        self.extension = extension;
    def getFullPath(self):
        return self.directory+"/"+self.fileName;
    def getCoreFileNameAndExtension(self):
        return self.coreFileName+self.extension;
    def getCoreFileNameWithTransformation(self, transformation=lambda x: x):
        return transformation(self.coreFileName);
    def getFileNameWithTransformation(self,transformation,extension=None):
        toReturn = self.getCoreFileNameWithTransformation(transformation);
        if (extension is not None):
            toReturn = toReturn+extension;
        else:
            if (self.extension is not None):
                toReturn = toReturn+self.extension;
        return toReturn;
    def getFilePathWithTransformation(self,transformation=lambda x: x,extension=None):
        return self.directory+"/"+self.getFileNameWithTransformation(transformation,extension=extension);


def getFileHandle(filename,mode="r"):
    if (re.search('.gz$',filename) or re.search('.gzip',filename)):
        if (mode=="r"):
            mode="rb";
        return gzip.open(filename,mode)
    else:
        return open(filename,mode) 

#returns an array of all filter variables.
def splitLinesIntoOtherFiles(fileHandle, preprocessingStep, filterVariableFromLine, outputFilePathFromFilterVariable):
    filterVariablesToReturn = []
    filterVariableToOutputFileHandle = {};
    for line in fileHandle:
        processedLine = line;
        if (preprocessingStep is not None):
            processedLine = preprocessingStep(processedLine);
        filterVariable = filterVariableFromLine(processedLine);
        if (filterVariable not in filterVariableToOutputFileHandle):
            outputFilePath = outputFilePathFromFilterVariable(filterVariable);
            filterVariablesToReturn.append(filterVariable);
            outputFileHandle = getFileHandle(outputFilePath, 'w');
            filterVariableToOutputFileHandle[filterVariable] = outputFileHandle;
        outputFileHandle = filterVariableToOutputFileHandle[filterVariable];
        outputFileHandle.write(line)
    for fileHandle in filterVariableToOutputFileHandle.items():
        fileHandle[1].close();
    return filterVariablesToReturn;

#transformation has a specified default so that this can be used to, for instance, unzip a gzipped file.
def transformFile(
        fileHandle
        , outputFile
        , transformation=lambda x: x
        , progressUpdates=None
        , outputTitleFromInputTitle=None
        , ignoreInputTitle=False
        , filterFunction=None #should be some function of the line and the line number
        , preprocessing=None #processing to be applied before filterFunction AND transformation
    ):
    
    outputFileHandle = getFileHandle(outputFile, 'w');
    i = 0;
    action = lambda inp,i: outputFileHandle.write(inp);
    for line in fileHandle:
        i += 1;
        if (i == 1):
            if (outputTitleFromInputTitle is not None):
                outputFileHandle.write(outputTitleFromInputTitle(line));        
        processLine(line,i,ignoreInputTitle,preprocessing,filterFunction,transformation,action);
        printProgress(progressUpdates, i);
    outputFileHandle.close();

#reades a line of the file on-demand.
class FileReader:
    def __init__(self, fileHandle, preprocessing=None, filterFunction=None, transformation=lambda x: x, ignoreInputTitle=False):
        self.fileHandle = fileHandle;
        self.preprocessing = preprocessing;
        self.filterFunction = filterFunction;
        self.transformation = transformation;
        self.ignoreInputTitle = ignoreInputTitle;
        self.i = 0;
        self.eof = False;    
    def getNextLine(self):
        line=self.fileHandle.readline();
        if (line != ""): #empty string is eof...
            self.i += 1;
            if (self.i == 1):
                if (self.ignoreInputTitle == True):
                    self.title = line;
                    return self.getNextLine();
            
            def action(x,i): #to be passed into processLine
                self.toReturn = x;

            processLine(
                line=line
                ,i=self.i
                ,ignoreInputTitle=self.ignoreInputTitle
                ,preprocessing=self.preprocessing
                ,filterFunction=self.filterFunction
                ,transformation=self.transformation
                ,action=action);

            return self.toReturn;
        else:
            self.eof=True;
            return None;
    
def writeToFile(outputFile, contents):
    outputFileHandle = getFileHandle(outputFile, 'w');
    outputFileHandle.write(contents);
    outputFileHandle.close();

def transformFileIntoArray(fileHandle
    , transformation=lambda x: x
    , progressUpdates=None
    , ignoreInputTitle=False
    , filterFunction=None
    , preprocessing=None):
    i = 0;
    toReturn = [];
    action = lambda x,i: toReturn.append(x); #i is the line number
    performActionOnEachLineOfFile(fileHandle,action,transformation,progressUpdates,ignoreInputTitle,filterFunction,preprocessing);
    return toReturn;
            
def performActionOnEachLineOfFile(fileHandle
    , action=None #should be a function that accepts the preprocessed/filtered line and the line number
    , transformation=lambda x: x
    , progressUpdates=None
    , ignoreInputTitle=False
    , filterFunction=None
    , preprocessing=None #the preprocessing step is performed before both 'filterFunction' and 'transformation'. Originally I just had 'transformation'. 
    , actionFromTitle=None
    , progressUpdate=None):
    if (actionFromTitle is None and action is None):
        raise ValueError("One of actionFromTitle or action should not be None");
    if (actionFromTitle is not None and action is not None):
        raise ValueError("Only one of actionFromTitle or action can be non-None");
    if (actionFromTitle is not None and ignoreInputTitle == False):
        raise ValueError("If actionFromTitle is not None, ignoreInputTitle should probably be True because it implies a title is present");
    
    i = 0;
    for line in fileHandle:
        i += 1;
        if (i == 1 and actionFromTitle is not None):
            action = actionFromTitle(line);
        processLine(line,i,ignoreInputTitle,preprocessing,filterFunction,transformation,action, progressUpdate);
        printProgress(progressUpdates, i);

    fileHandle.close();

def processLine(line,i,ignoreInputTitle,preprocessing,filterFunction,transformation,action, progressUpdate=None):
    if (i > 1 or (ignoreInputTitle==False)):
        if progressUpdate is not None:
            if i%progressUpdate == 0:
                print "Done ",i,"lines";
        if (preprocessing is not None):
            line = preprocessing(line);
        if (filterFunction is None or filterFunction(line,i)):
            action(transformation(line),i)

def printProgress(progressUpdates, i):
    if progressUpdates is not None:
        if (i%progressUpdates == 0):
            print "Processed "+str(i)+" lines";

def defaultTabSeppd(s):
    s = trimNewline(s);
    s = splitByTabs(s);
    return s;

def trimNewline(s):
    return s.rstrip('\r\n');

def appendNewline(s):
    return s+"\n"; #aargh O(n) aargh FIXME if you can

def splitByDelimiter(s,delimiter):
    return s.split(delimiter);

def splitByTabs(s):
    return splitByDelimiter(s,"\t");

def stringToFloat(s):
    return float(s);

def stringToInt(s):
    return int(s);

def lambdaMaker_getAtPosition(index):
    return (lambda x: x[index]);

def lambdaMaker_insertSuffixIntoFileName(suffix,separator):
    return lambda fileName: getFileNameParts(fileName).getFileNameWithTransformation(
            lambda coreFileName: coreFileName+separator+suffix
    );
def lambdaMaker_insertPrefixIntoFileName(prefix, separator):
    return lambda fileName: getFileNameParts(fileName).getFileNameWithTransformation(
        lambda coreFileName: prefix+separator+coreFileName
    );

def simpleDictionaryFromFile(fileHandle, keyIndex, valIndex, titlePresent=False, transformation=defaultTabSeppd):
    toReturn = {};
    def action(inp, lineNumber):
        toReturn[inp[keyIndex]] = inp[valIndex];
    performActionOnEachLineOfFile(
        fileHandle=fileHandle
        ,action=action
        ,transformation=transformation
        ,ignoreInputTitle=titlePresent
    );
    return toReturn;

'''Accepts a title, uses it to produce a function that generates a dictionary given an array'''
def lambdaMaker_dictionaryFromLine(title,delimiter="\t"):
    lineToArr = util.chainFunctions(trimNewline,lambda x: splitByDelimiter(x,delimiter));
    splitTitle = lineToArr(title);
    def lineToDictionary(line):
        toReturn = {};
        for entry in enumerate(lineToArr(line)):
            toReturn[splitTitle[entry[0]]] = entry[1];
        return toReturn;
    return lineToDictionary;

#wrapper for the cat command
def concatenateFiles(outputFile, arrOfFilesToConcatenate):
    util.executeAsSystemCall("cat "+(" ".join(arrOfFilesToConcatenate))+" > "+outputFile);

def concatenateFiles_preprocess(
    outputFile
    , arrOfFilesToConcatenate
    , transformation=lambda x,y: x #x is the input line, y is the transformed input file name (see inputFileNameTransformation)
    , inputFileTransformation=lambda x: getFileNameParts(x).coreFileName # the function that transforms the path of the input file
    , outputTitleFromInputTitle = None #function that takes input title and transforms into output title. Considers title of first file in line.
    , ignoreInputTitle=False #really unfortunately named. Should have been named 'titlePresent'
    ):
    inputTitle = None;
    outputFileHandle = getFileHandle(outputFile, 'w');
    for aFile in arrOfFilesToConcatenate:
        transformedInputFilename = inputFileTransformation(aFile);
        aFileHandle = getFileHandle(aFile);
        i = 0;
        for line in aFileHandle:
            i += 1;
            if (i == 1):
                if (outputTitleFromInputTitle is not None):
                    if (inputTitle is None):
                        inputTitle = line;
                        outputFileHandle.write(outputTitleFromInputTitle(inputTitle));    
            if (i > 1 or (ignoreInputTitle==False)):
                outputFileHandle.write(transformation(line, transformedInputFilename));
    outputFileHandle.close();

def readRowsIntoArr(fileHandle,progressUpdate=None):
    arr = [];
    def action(inp,lineNumber):
        if progressUpdate is not None:
            if (lineNumber%progressUpdate == 0):
                print "processed "+str(lineNumber)+" lines";
        arr.append(inp); 
    performActionOnEachLineOfFile(
        fileHandle
        , transformation=trimNewline
        , action=action
        , ignoreInputTitle=False
    );
    return arr;

def readColIntoArr(fileHandle,col=0,titlePresent=True):
    arr = [];
    def action(inp, lineNumber):
        arr.append(inp[col]);
    performActionOnEachLineOfFile(
        fileHandle
        , transformation=defaultTabSeppd
        , action=action
        , ignoreInputTitle=titlePresent
    );
    return arr;

def read2DMatrix(fileHandle,colNamesPresent=False,rowNamesPresent=False,contentType=float, contentStartIndex=1,progressUpdate=None):
    """
        returns an instance of util.Titled2DMatrix
    """
    titled2DMatrix = util.Titled2DMatrix(colNamesPresent=colNamesPresent, rowNamesPresent=rowNamesPresent);
    def action(inp, lineNumber):
        if (lineNumber==1 and colNamesPresent):
            titled2DMatrix.setColNames(inp[contentStartIndex:]);
        else:
            rowName = inp[0] if rowNamesPresent else None;
            arr = [contentType(x) for x in inp[contentStartIndex:]]; #ignore the column denoting the name of the row
            titled2DMatrix.addRow(arr, rowName=rowName);
    performActionOnEachLineOfFile(
        fileHandle=fileHandle
        ,action=action
        ,transformation=defaultTabSeppd
        ,ignoreInputTitle=False
        ,progressUpdate=progressUpdate
    ); 
    return titled2DMatrix;

#will trim the newline for you
def titleColumnToIndex(title,sep="\t"):
    title = trimNewline(title);
    title = title.split(sep);
    return util.valToIndexMap(title);
