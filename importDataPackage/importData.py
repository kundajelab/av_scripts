import sys;
import os;
import pdb; 
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
sys.path.insert(0,scriptsDir+"/importDataPackage");
import pathSetter;
import util;
import fileProcessing as fp;
from collections import namedtuple;
from collections import OrderedDict;
import numpy as np;

#I don't use this class anymore
class LabelRepresentationCounter(object):
    def __init__(self):
        self.posExamples = 0;
        self.negExamples = 0;
    def update(self, val):
        assert val == 0 or val == 1;
        if (val == 0):
            self.negExamples += 1;
        if (val == 1):
            self.posExamples += 1;
    def merge(self,otherCounter):
        toReturn = LabelRepresentationCounter();
        toReturn.posExamples = self.posExamples + otherCounter.posExamples;
        toReturn.negExamples = self.negExamples + otherCounter.negExamples;
        return toReturn;
    def finalise(self): #TODO: normalise so that the weight is even across tissue labels
        self.positiveWeight = 0 if self.posExamples == 0 else float(self.posExamples + self.negExamples)/(self.posExamples);
        self.negativeWeight = 0 if self.negExamples == 0 else float(self.posExamples + self.negExamples)/(self.negExamples);

class DynamicEnum(object):
    """
        just a wrapper around a dictionary, so that the keys are
        accessible using the object attribute syntax rather
        than the dictionary syntax.
    """
    def __init__(self, *keys):
        self._valsDict = OrderedDict();
    def addKey(self, keyName, val):
        setattr(self, keyName, val);
        self._valsDict[keyName] = val;
    def getKey(self, keyName):
        return self._valsDict[keyName];
    def hasKey(self, keyName):
        if keyName not in self._valsDict:
            return False;
        return True;
    def getKeys(self):
        return self._valsDict.keys();

class UNDEF(object):
    pass;

class Key(object):
    def __init__(self, keyNameInternal, keyNameExternal=None, default=UNDEF):
        self.keyNameInternal = keyNameInternal;
        if (keyNameExternal is None):
            keyNameExternal = keyNameInternal;
        self.keyNameExternal = keyNameExternal;
        self.default=default;

class Keys(object): #I am keeping a different external and internal name for the flexibility of changing the external name in the future.
    #the advantage of having a class like this rather than just using enums is being able to support
    #methods like "fillInDefaultsForKeys".
    #I need the DynamicEnum class so that I can use the Keys class for different types of Keys; i.e. I don't
    #know what the keys are going to be beforehand and I don't know how else to create an enum dynamically.
    def __init__(self, *keys):
        self.keys = DynamicEnum(); #just a wrapper around a dictionary, for the purpose of accessing the keys using the object attribute syntax rather than the dictionary syntax.
        self.keysDefaults = DynamicEnum();
        for key in keys:
            self.addKey(key.keyNameInternal, key.keyNameExternal, key.default);
    def addKey(self, keyNameInternal, keyNameExternal, defaultValue=UNDEF):
        self.keys.addKey(keyNameInternal, keyNameExternal);
        if (defaultValue != UNDEF):
            self.keysDefaults.addKey(keyNameInternal, defaultValue);
    def checkForUnsupportedKeys(self, aDict):
        for aKey in aDict:
            if self.keys.hasKey(aKey)==False:
                raise RuntimeError("Unsupported key "+str(aKey)+"; supported keys are: "+str(self.keys.getKeys()));
    def fillInDefaultsForKeys(self, aDict, internalNamesOfKeysToFillDefaultsFor=None):
        if internalNamesOfKeysToFillDefaultsFor is None:
            internalNamesOfKeysToFillDefaultsFor = self.keys.getKeys();
        for aKey in internalNamesOfKeysToFillDefaultsFor:
            if aKey not in aDict:
                if (self.keysDefaults.hasKey(aKey)==False):
                    raise RuntimeError("Default for "+str(aKey)+" not present, and a value was not provided");
                aDict[aKey] = self.keysDefaults.getKey(aKey);
        return aDict;
    def checkForUnsupportedKeysAndFillInDefaults(self, aDict):
        self.checkForUnsupportedKeys(aDict)
        self.fillInDefaultsForKeys(aDict);

#something like pytable is sufficiently different that
#we can assume all this loading is for in-memory situations
ContentType=namedtuple('ContentType',['name','castingFunction']);
ContentTypes=util.enum(integer=ContentType("int",int),floating=ContentType("float",float),string=ContentType("str",str));
ContentTypesLookup = dict((x.name,x.castingFunction) for x in ContentTypes.vals);
RootKeys=Keys(Key("features"), Key("labels"), Key("splits"), Key("weights"));
FeaturesFormat=util.enum(rowsAndColumns='rowsAndColumns'
                         , fasta='fasta'
                         , fastaInCol="fastaInCol"
                         , signalFromBigWig="signalFromBigWig"); 
DefaultModeNames = util.enum(labels="defaultOutputModeName", features="defaultInputModeName");
FeaturesKeys = Keys(Key("featuresFormat")
                    , Key("opts")
                    , Key("inputModeName", default=DefaultModeNames.features));
FeatureSetYamlKeys_RowsAndCols = Keys(
    Key("fileNames")
    ,Key("contentType",default=ContentTypes.floating.name)
    ,Key("contentStartIndex",default=1)
    ,Key("subsetOfColumnsToUseOptions",default=None)
    ,Key("progressUpdate",default=None));
#For files that have the format produced by getfasta bedtools; >key \n [fasta sequence] \n ...
FeatureSetYamlKeys_Fasta = Keys(Key("fileNames"), Key("progressUpdate",default=None));
#For files that have the sequence in a specific column of the file
FeatureSetYamlKeys_FastaInCol = Keys(Key("fileNames"), Key("seqNameCol",default=0), Key("seqCol",default=1),Key("progressUpdate",default=None), Key("titlePresent",default=False));
FeatureSetYamlKeys_SignalFromBigWig = Keys(Key("coordinateFiles")
                                          , Key("bigWigFilePath")
                                          , Key("chromCol", 0)
                                          , Key("startCol", 1)
                                          , Key("endCol", 2)
                                          , Key("progressUpdate",default=None)
                                          , Key("titlePresent",default=False));
SubsetOfColumnsToUseOptionsYamlKeys = Keys(Key("subsetOfColumnsToUseMode"), Key("fileWithColumnNames",default=None), Key("N", default=None)); 
#subset of cols modes: setOfColumnNames, topN

def getSplitNameToInputDataFromSeriesOfYamls(seriesOfYamls):
    import itertools
    #if some of the things in seriesOfYamls are lists, chain together
    seriesOfYamls = list(itertools.chain(*[x if isinstance(x,list) else [x] for x in seriesOfYamls]))
    combinedYaml=getCombinedYamlFromSeriesOfYamls(seriesOfYamls);
    return getSplitNameToInputDataFromCombinedYaml(combinedYaml);

def getCombinedYamlFromSeriesOfYamls(seriesOfYamls):
    #if there are, for instance, multiple feature yamls and/or
    #multiple label yamls, will condense them.
    combinedYaml = OrderedDict([('features',[]), ('labels',[]), ('weights',[])]);
    #the contents of the yaml file must be a dictionaries where
    #the keys at the root are one of RootKeys.keys, which are
    #at the time of writing: 'features', 'labels' or 'splits' 
    for yamlObject in seriesOfYamls:
        RootKeys.checkForUnsupportedKeys(yamlObject);
        for key in [RootKeys.keys.features, RootKeys.keys.labels, RootKeys.keys.weights]:
            if (key in yamlObject):
                combinedYaml[key].append(yamlObject[key]);
        for key in [RootKeys.keys.splits]:
            if key in yamlObject:
                if key not in combinedYaml:
                    combinedYaml[key] = yamlObject[key];
                else:
                    raise RuntimeError("Two specifications given for "+str(key));
    return combinedYaml;

def getSplitNameToInputDataFromCombinedYaml(combinedYaml):
    idToSplitNames,distinctSplitNames = getIdToSplitNames(combinedYaml[RootKeys.keys.splits]);
    outputModeNameToIdToLabels, outputModeNameToLabelNames = getIdToLabels(combinedYaml[RootKeys.keys.labels]);
    if (RootKeys.keys.weights in combinedYaml):
        outputModeNameToIdToWeights, outputModeNameToWeightNames = getIdToWeights(combinedYaml[RootKeys.keys.weights]);
    else:
        outputModeNameToIdToWeights, outputModeNameToWeightNames = None, None;
    outputModeNames = outputModeNameToIdToLabels.keys()
    inputModeNames = []
    for featuresYamlObject in combinedYaml[RootKeys.keys.features]:
        FeaturesKeys.fillInDefaultsForKeys(featuresYamlObject);
        FeaturesKeys.checkForUnsupportedKeys(featuresYamlObject);
        inputModeNames.append(featuresYamlObject[FeaturesKeys.keys.inputModeName]);
    splitNameToDfsc = dict((x, DataForSplitCompiler(
                                    inputModeNames=inputModeNames
                                    ,outputModeNames=outputModeNames
                                    ,outputModeNameToLabelNames=outputModeNameToLabelNames
                                    ,outputModeNameToWeights=outputModeNameToWeightNames))\
                                    for x in distinctSplitNames);
    for featuresYamlObject in combinedYaml[RootKeys.keys.features]:
        updateSplitNameToDfscUsingFeaturesYamlObject(featuresYamlObject
                                                        , idToSplitNames
                                                        , outputModeNameToIdToLabels
                                                        , outputModeNameToIdToWeights
                                                        , splitNameToDfsc);
    print("Returning desired dict");
    toReturn = dict((x,splitNameToDfsc[x].getInputData()) for x in splitNameToDfsc);
    #do a check to see if any of the ids in idToSplitNames were not represented in the final
    #data.
    idsThatDidNotMakeIt = [];
    #compile a list of ids that made it across train, test and valid data
    idsThatMadeIt = dict((theId,1) for inputData in toReturn.values() for theId in inputData.ids);
    for anId in idToSplitNames:
        if anId not in idsThatMadeIt:
            idsThatDidNotMakeIt.append(anId);
    if len(idsThatDidNotMakeIt)>0:
        print("WARNING.",len(idsThatDidNotMakeIt)," ids in the train/test/valid split files were not found in the"
              " input feature file. The first ten are: ",idsThatDidNotMakeIt[:10]); 
    return toReturn;

SplitOptsKeys = Keys(Key("titlePresent",default=False),Key("col",default=0)); 
SplitKeys = Keys(Key("splitNameToSplitFiles"), Key("opts", default=SplitOptsKeys.fillInDefaultsForKeys({})));

def getIdToSplitNames(splitObject):
    """
        return:
        idToSplitNames
        distinctSplitNames
    """
    SplitKeys.fillInDefaultsForKeys(splitObject);
    SplitKeys.checkForUnsupportedKeys(splitObject);
    opts = splitObject[SplitKeys.keys.opts]; 
    SplitOptsKeys.fillInDefaultsForKeys(opts);
    SplitOptsKeys.checkForUnsupportedKeys(opts);   
    splitNameToSplitFile = splitObject[SplitKeys.keys.splitNameToSplitFiles]; 
    idToSplitNames = {};
    distinctSplitNames = [];
    for splitName in splitNameToSplitFile:
        if splitName in distinctSplitNames:
            raise RuntimeError("Repeated splitName: "+str(splitName));
        distinctSplitNames.append(splitName);
        idsInSplit = fp.readColIntoArr(fp.getFileHandle(splitNameToSplitFile[splitName]), **opts);
        for theId in idsInSplit:
            if theId not in idToSplitNames:
                idToSplitNames[theId] = [];
            idToSplitNames[theId].append(splitName);
    return idToSplitNames, distinctSplitNames;

WeightsKeys=Keys(Key("weights"), Key("outputModeName", default=DefaultModeNames.labels)) 
def getIdToWeights(weightsObjects): 
    outputModeNameToIdToWeights= OrderedDict();
    outputModeNameToWeightNames = OrderedDict();
    for weightsObject in weightsObjects:
        WeightsKeys.fillInDefaultsForKeys(weightsObject);
        WeightsKeys.checkForUnsupportedKeys(weightsObject);
        outputModeName = weightsObject[WeightsKeys.keys.outputModeName] 
        titledMappingObject = fp.readTitledMapping(fp.getFileHandle(weightsObject[WeightsKeys.keys.weights]))
        outputModeNameToIdToWeights[outputModeName] = titledMappingObject.mapping
        outputModeNameToWeightNames[outputModeName] = titledMappingObject.titleArr
    return outputModeNameToIdToWeights, outputModeNameToWeightNames, 

#fp.readTitledMapping(fp.getFileHandle(metadataFile), contentType=str, subsetOfColumnsToUseOptions=fp.SubsetOfColumnsToUseOptions(columnNames=relevantColumns))
LabelsKeys = Keys(Key("fileName")
                 , Key("contentType", default=ContentTypes.integer.name)
                 , Key("fileWithLabelsToUse",default=None)
                 , Key("keyColumns",default=[0])
                 , Key("outputModeName", default=DefaultModeNames.labels));
def getIdToLabels(labelsObjects):
    """
        accepts a bunch of labels yaml objects, each of which corresponds to
            a different output mode.
        return: outputModeNameToIdToLabels, outputModeNameToLabelNames
    """
    outputModeNameToIdToLabels= OrderedDict();
    outputModeNameToLabelNames = OrderedDict();
    for labelsObject in labelsObjects:
        LabelsKeys.fillInDefaultsForKeys(labelsObject);
        LabelsKeys.checkForUnsupportedKeys(labelsObject);
        outputModeName = labelsObject[LabelsKeys.keys.outputModeName] 
        titledMappingObject = getIdToLabels_singleLabelSet(labelsObject)
        outputModeNameToIdToLabels[outputModeName] = titledMappingObject.mapping
        outputModeNameToLabelNames[outputModeName] = titledMappingObject.titleArr
    return outputModeNameToIdToLabels, outputModeNameToLabelNames, 

def getIdToLabels_singleLabelSet(labelsObject):
    """
        return: titledMapping which has attributes:
            .mapping = idToLabels dictionary
            .titleArr = label names.
    """
    fileWithLabelsToUse = labelsObject[LabelsKeys.keys.fileWithLabelsToUse];
    titledMapping = fp.readTitledMapping(fp.getFileHandle(labelsObject[LabelsKeys.keys.fileName])
                                            , contentType=getContentTypeFromName(labelsObject[LabelsKeys.keys.contentType])
                                            , keyColumns = labelsObject[LabelsKeys.keys.keyColumns]
                                            , subsetOfColumnsToUseOptions=\
                                                None if fileWithLabelsToUse is None else fp.SubsetOfColumnsToUseOptions(
                                                    columnNames=fp.readRowsIntoArr(fp.getFileHandle(fileWithLabelsToUse)) 
                                            ));
    return titledMapping;
    

def getContentTypeFromName(contentTypeName):
    if contentTypeName not in ContentTypesLookup:
        raise RuntimeError("Unsupported content type: "+str(contentTypeName)); 
    return ContentTypesLookup[contentTypeName];

def updateSplitNameToDfscUsingFeaturesYamlObject(
                                    featuresYamlObject
                                    , idToSplitNames
                                    , outputModeNameToIdToLabels
                                    , outputModeNameToIdToWeights
                                    , splitNameToDfsc):
    fileFormat = featuresYamlObject[FeaturesKeys.keys.featuresFormat];
    inputModeName = featuresYamlObject[FeaturesKeys.keys.inputModeName];
    opts = featuresYamlObject[FeaturesKeys.keys.opts];
    if (fileFormat == FeaturesFormat.rowsAndColumns):
        compilerFunc=updateSplitNameToDfscUsingFeaturesYamlObject_RowsAndCols;
    elif (fileFormat == FeaturesFormat.fasta):
        compilerFunc=updateSplitNameToDfscUsingFeaturesYamlObject_Fasta;
    elif (fileFormat == FeaturesFormat.fastaInCol):
        compilerFunc=updateSplitNameToDfscUsingFeaturesYamlObject_FastaInCol;
    elif (fileFormat == FeaturesFormat.signalFromBigWig):
        compilerFunc=updateSplitNameToDfscUsingFeaturesYamlObject_SignalFromBigWig;
    else:
        raise RuntimeError("Unsupported features file format: "+str(fileFormat));
    compilerFunc(inputModeName, opts, idToSplitNames, outputModeNameToIdToLabels, outputModeNameToIdToWeights, splitNameToDfsc);

def featurePreparationActionOnFiles(fileNames, featurePreparationActionOnFileHandle):
    """
        will execute featurePreparationActionOnFileHandle on every file
            in fileNames, and will count the total number of feature records that are
            skipped and print them out at the end.
    """
    for (fileNumber, fileName) in enumerate(fileNames):
        skippedFeatureRowsWrapper = util.VariableWrapper(0); #a variable that will count the num of skipped rows
        fileHandle = fp.getFileHandle(fileName);
        featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper);
        print(skippedFeatureRowsWrapper.var,"rows skipped from",fileName); 

def updateDataForSplit(
        inputModeName, theId
        , featureProducer, skippedFeatureRowsWrapper
        , idToSplitNames
        , outputModeNameToIdToLabels
        , outputModeNameToIdToWeights
        , splitNameToDfsc):
    """
        calls 'update' on a SplitNameToDfsc object
    """
    if (theId in idToSplitNames):
        for splitName in idToSplitNames[theId]:
            splitNameToDfsc[splitName].update(inputModeName=inputModeName
                                                  , theId=theId
                                                  , featuresForModeAndId=featureProducer()
                                                  , outputModeNameToLabelsForId=
                                                     {outputModeName:
                                                        outputModeNameToIdToLabels[outputModeName][theId]
                                                      for outputModeName in outputModeNameToIdToLabels}
                                                  , outputModeNameToWeightsForId=
                                                     (None if outputModeNameToIdToWeights is None else
                                                      {outputModeName:
                                                            outputModeNameToIdToWeights[outputModeName][theId]
                                                      for outputModeName in outputModeNameToIdToWeights}));
    else:
        if (skippedFeatureRowsWrapper.var == 0):
            print("WARNING.",theId,"was not found in train/test/valid splits");
            print("This is the only time such a warning will be printed. Remaining "
                  "such ids will be silently ignored");
        skippedFeatureRowsWrapper.var += 1; 
    
def updateSplitNameToDfscUsingFeaturesYamlObject_RowsAndCols(inputModeName
                                                                , featureSetYamlObject
                                                                , idToSplitNames
                                                                , outputModeNameToIdToLabels
                                                                , outputModeNameToIdToWeights
                                                                , splitNameToDfsc):
    """
        Use the data in a file where the features are stored as rows and columns to update the splits.
    """
    KeysObj = FeatureSetYamlKeys_RowsAndCols;
    KeysObj.checkForUnsupportedKeysAndFillInDefaults(featureSetYamlObject)
    subsetOfColumnsToUseOptions = (None if featureSetYamlObject[KeysObj.keys.subsetOfColumnsToUseOptions] is None
                                    else createSubsetOfColumnsToUseOptionsFromYamlObject(
                                            featureSetYamlObject[KeysObj.keys.subsetOfColumnsToUseOptions])); 
    contentType = getContentTypeFromName(featureSetYamlObject[KeysObj.keys.contentType]);
    contentStartIndex = featureSetYamlObject[KeysObj.keys.contentStartIndex];
    
    def featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper):
        coreTitledMappingAction = fp.getCoreTitledMappingAction(subsetOfColumnsToUseOptions=subsetOfColumnsToUseOptions, contentType=contentType, contentStartIndex=contentStartIndex);
        def action(inp, lineNumber):
            if (lineNumber==1):
                #If this is the first row, then update the list of predictor names using the names in the title.
                featureNames = coreTitledMappingAction(inp, lineNumber); 
                if (fileNumber==0):
                    for splitName in splitNameToDfsc:
                        splitNameToDfsc[splitName].extendFeatureNames(inputModeName, featureNames);
            else:
                #otherwise, just update the features.
                theId, features = coreTitledMappingAction(inp, lineNumber);
                updateDataForSplit(inputModeName=inputModeName
                                    , theId=theId
                                    , featureProducer=lambda: list(features)
                                    , skippedFeatureRowsWrapper=skippedFeatureRowsWrapper
                                    , idToSplitNames=idToSplitNames
                                    , outputModeNameToIdToLabels=outputModeNameToIdToLabels
                                    , outputModeNameToIdToWeights=outputModeNameToIdToWeights
                                    , splitNameToDfsc=splitNameToDfsc);
        fp.performActionOnEachLineOfFile(
            fileHandle=fileHandle
            ,action=action
            ,transformation=fp.defaultTabSeppd
            ,progressUpdate=featureSetYamlObject[KeysObj.keys.progressUpdate]
        );

    featurePreparationActionOnFiles(featureSetYamlObject[KeysObj.keys.fileNames], featurePreparationActionOnFileHandle);

def updateSplitNameToDfscUsingFeaturesYamlObject_Fasta(inputModeName
                                                            , featureSetYamlObject
                                                            , idToSplitNames
                                                            , outputModeNameToIdToLabels
                                                            , outputModeNameToIdToWeights
                                                            , splitNameToDfsc):
    """
        Use the data in a file where the features are fasta rows; the fasta file will be converted to a 2D image.
    """
    KeysObj = FeatureSetYamlKeys_Fasta;
    KeysObj.checkForUnsupportedKeysAndFillInDefaults(featureSetYamlObject)
    def featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper):
        fastaIterator = fp.FastaIterator(fileHandle, progressUpdate=featureSetYamlObject[KeysObj.keys.progressUpdate], progressUpdateFileName=fileName);
        for (seqNumber, (seqName, seq)) in enumerate(fastaIterator):
            #in the case of this dataset, I'm not going to try to update predictorNames as it's going to be the 2D image thing.
            updateDataForSplit(inputModeName=inputModeName
                                , theId=seqName
                                , featureProducer=lambda: util.seqTo2Dimage(seq)
                                , skippedFeatureRowsWrapper=skippedFeatureRowsWrapper
                                , idToSplitNames=idToSplitNames
                                , outputModeNameToIdToLabels=outputModeNameToIdToLabels
                                , outputModeNameToIdToWeights=outputModeNameToIdToWeights
                                , splitNameToDfsc=splitNameToDfsc);
    featurePreparationActionOnFiles(featureSetYamlObject[KeysObj.keys.fileNames], featurePreparationActionOnFileHandle);
    print("Done loading in fastas");

def updateSplitNameToDfscUsingFeaturesYamlObject_FastaInCol(inputModeName
                                                                , featureSetYamlObject
                                                                , idToSplitNames
                                                                , outputModeNameToIdToLabels
                                                                , outputModeNameToIdToWeights
                                                                , splitNameToDfsc):
    """
        Use the data in a file where the features are fasta rows; the fasta file will be converted to a 2D image.
    """
    KeysObj = FeatureSetYamlKeys_FastaInCol;
    KeysObj.checkForUnsupportedKeysAndFillInDefaults(featureSetYamlObject);
    def featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper):
        fileHandle = fp.getFileHandle(fileName);
        def action(inp, lineNumber):
            seqName = inp[featureSetYamlObject[KeysObj.keys.seqNameCol]]; 
            seq = inp[featureSetYamlObject[KeysObj.keys.seqCol]];
            updateDataForSplit(inputModeName=inputModeName
                                , theId=seqName
                                , featureProducer=lambda: util.seqTo2Dimage(seq)
                                , skippedFeatureRowsWrapper=skippedFeatureRowsWrapper
                                , idToSplitNames=idToSplitNames
                                , outputModeNameToIdToLabels=outputModeNameToIdToLabels
                                , outputModeNameToIdToWeights=outputModeNameToIdToWeights
                                , splitNameToDfsc=splitNameToDfsc);
        fp.performActionOnEachLineOfFile(fileHandle = fileHandle
                                        , action=action, transformation=fp.defaultTabSeppd
                                        , progressUpdateFileName=featureSetYamlObject[KeysObj.keys.progressUpdate]
                                        , ignoreInputTitle=featureSetYamlObject[KeysObj.keys.titlePresent]);
    featurePreparationActionOnFiles(featureSetYamlObject[KeysObj.keys.fileNames], featurePreparationActionOnFileHandle);

def updateSplitNameToDfscUsingFeaturesYamlObject_SignalFromBigWig(inputModeName
                                                                , featureSetYamlObject
                                                                , idToSplitNames
                                                                , outputModeNameToIdToLabels
                                                                , outputModeNameToIdToWeights
                                                                , splitNameToDfsc):
    import bx.bbi.bigwig_file;  
    """
        1d signal extracted from a bigwig track
    """
    KeysObj = FeatureSetYamlKeys_SignalFromBigWig;
    KeysObj.checkForUnsupportedKeysAndFillInDefaults(featureSetYamlObject);
    bigWigFilePath = featureSetYamlObject[KeysObj.keys.bigWigFilePath];
    bigWigReader = bx.bbi.bigwig_file.BigWigFile(fp.getFileHandle(bigWigFilePath));
    def getDataForRegion(chrom, start, end):
        #based on https://bitbucket.org/james_taylor/bx-python/src/38dc8eb987fb/lib/bx/bbi/bigwig_tests.py?fileviewer=file-view-default
        data = bigWigReader.summarize(chrom, start, end, 1) 
        return data.sum_data;
    def featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper):
        fileHandle = fp.getFileHandle(fileName);
        def action(inp, lineNumber):
            chrom = inp[featureSetYamlObject[KeysObj.keys.chromCol]]; 
            start = inp[featureSetYamlObject[KeysObj.keys.startCol]]; 
            end = inp[featureSetYamlObject[KeysObj.keys.endCol]]; 
            updateDataForSplit(inputModeName=inputModeName
                                , theId=seqName
                                , featureProducer=lambda:\
                                    getDataForRegion(chrom, start, end)[None, None, :]
                                , skippedFeatureRowsWrapper=skippedFeatureRowsWrapper
                                , idToSplitNames=idToSplitNames
                                , outputModeNameToIdToLabels=outputModeNameToIdToLabels
                                , outputModeNameToIdToWeights=outputModeNameToIdToWeights
                                , splitNameToDfsc=splitNameToDfsc);
        fp.performActionOnEachLineOfFile(fileHandle = fileHandle
                                        , action=action, transformation=fp.defaultTabSeppd
                                        , progressUpdateFileName=featureSetYamlObject[KeysObj.keys.progressUpdate]
                                        , ignoreInputTitle=featureSetYamlObject[KeysObj.keys.titlePresent]);
    featurePreparationActionOnFiles(featureSetYamlObject[KeysObj.keys.fileNames], featurePreparationActionOnFileHandle);

SubsetOfColumnsToUseOptionsYamlKeys = Keys(Key("subsetOfColumnsToUseMode"), Key("fileWithColumnNames",default=None), Key("N", default=None)); 
def createSubsetOfColumnsToUseOptionsFromYamlObject(subsetOfColumnsToUseYamlObject):
    """
        create fp.SubsetOfColumnsToUseOptions object from yaml devoted to it
    """
    SubsetOfColumnsToUseOptionsYamlKeys.checkForUnsupportedKeysAndFillInDefaults(subsetOfColumnsToUseYamlObject)
    mode = subsetOfColumnsToUseYamlObject[SubsetOfColumnsToUseOptionsYamlKeys.keys.subsetOfColumnsToUseMode];
    fileWithColumnNames = subsetOfColumnsToUseYamlObject[SubsetOfColumnsToUseOptionsYamlKeys.keys.fileWithColumnNames];
    N = subsetOfColumnsToUseYamlObject[SubsetOfColumnsToUseOptionsYamlKeys.keys.N];
    subsetOfColumnsToUseOptions = fp.SubsetOfColumnsToUseOptions(mode=mode
                                ,columnNames=None if fileWithColumnNames is None else fp.readRowsIntoArr(fp.getFileHandle(fileWithColumnNames))
                                ,N=N);
    return subsetOfColumnsToUseOptions;

class InputData(object): #store the final data for a particular train/test/valid slit
    """can't use namedtuple cos want members to be mutable"""
    def __init__(self, ids, X, Y, featureNames, labelNames, weights=None):
        """
            pretty sure I usually just set featureNames to None because it's a
                pain to bother with
            weights = per sample weights
        """
        self.ids = ids;
        self.X = X;
        self.Y = Y;
        self.featureNames = featureNames;
        self.labelNames = labelNames;
        self.weights=weights; 
    @staticmethod
    def concat(*inputDatas):
        ids = [y for inputData in inputDatas for y in inputData.ids];
        X = np.concatenate([inputData.X for inputData in inputDatas], axis=0);
        Y = np.concatenate([inputData.Y for inputData in inputDatas], axis=0);
        featureNames = inputDatas[0].featureNames;
        labelNames = inputDatas[0].labelNames
        return InputData(ids=ids, X=X, Y=Y
                        , featureNames=featureNames
                        , labelNames=labelNames);

class DataForSplitCompiler(object):
    """
        Compiles the data for a particular train/test/valid split; data is added via the update call
        At the end, call getInputData to finalise.
        Abbreviated "DFSC/Dfsc"
    """    
    def __init__(self
                , inputModeNames
                , outputModeNames=None
                , outputModeNameToLabelNames=None
                , outputModeNameToWeights=None):
        self.ids = [];
        self.idToIndex = {};
        self.inputModeNameToFeatureNames = {};
        self.outputModeNames=outputModeNames;
        self.outputModeNameToLabelNames=outputModeNameToLabelNames;
        self.outputModeNameToLabels= None if outputModeNames is None else\
            OrderedDict([(outputModeName,[]) for outputModeName in self.outputModeNames])
        self.outputModeNameToWeights = None if outputModeNames is None else\
            OrderedDict([(outputModeName,[]) for outputModeName in self.outputModeNames])
        self.inputModeNameToFeatures=\
            OrderedDict([(inputModeName,[]) for inputModeName in inputModeNames]);
        self.outputModeNameToLabelRepresentationCounters=\
            OrderedDict([(outputModeName, []) for outputModeName in self.outputModeNames]);
    def extendFeatureNames(self, inputMode, featureNames):
        if (inputMode not in self.inputModeNameToFeatureNames):
            self.inputModeNameToFeatureNames[inputMode] = [];
        self.inputModeNameToFeatureNames[inputMode].extend(featureNames);
    def getInputData(self):
        features = self.inputModeNameToFeatures;
        featureNames = self.inputModeNameToFeatureNames;
        labels = self.outputModeNameToLabels;
        weights = self.outputModeNameToWeights;
        for outputModeName in weights:
            if len(weights[outputModeName])==0:
                weights[outputModeName] = None;
            else:
                weights[outputModeName] = np.asarray(weights[outputModeName]).flatten();
        labelNames = self.outputModeNameToLabelNames;
        #in the case where it looks like there is just one mode, and it has
        #the default name, then remove it from the dictionary and just use
        #the value. 
        if (len(features.keys())==1 and DefaultModeNames.features in features):
            features = features[DefaultModeNames.features]; 
        if (len(featureNames.keys())==1 and DefaultModeNames.features in featureNames):
            featureNames = featureNames[DefaultModeNames.features];
        elif (len(featureNames.keys())==0):
            featureNames=None;
            
        if (len(labels.keys())==1 and DefaultModeNames.labels in labels):
            labels = labels[DefaultModeNames.labels];
            weights = weights[DefaultModeNames.labels];
            labelNames = labelNames[DefaultModeNames.labels];
        return InputData(ids=self.ids
                        , X=features
                        , Y=labels
                        , featureNames=featureNames
                        , labelNames=labelNames
                        , weights=weights);
    def update(self, inputModeName, theId
                   , featuresForModeAndId
                   , outputModeNameToLabelsForId=None
                   , outputModeNameToWeightsForId=None
                   , duplicatesDisallowed=True):
        #check if this is the first time we are seeing the id
        if (theId not in self.idToIndex): #if so
            #add to the list of ids to get a unique index for the id
            self.idToIndex[theId] = len(self.ids);
            self.ids.append(theId) 
            #also initialise the outputs for this id
            for (outputModeName) in self.outputModeNames:
                if (outputModeNameToLabelsForId is not None):
                    self.outputModeNameToLabels[outputModeName]\
                        .append(outputModeNameToLabelsForId[outputModeName]);
                if (outputModeNameToWeightsForId is not None):
                    if outputModeName in outputModeNameToWeightsForId:
                        self.outputModeNameToWeights[outputModeName]\
                            .append(outputModeNameToWeightsForId[outputModeName]);
        #obtain the index for the id
        idIdx = self.idToIndex[theId];
        #get the length of the array storing the features for this mode
        lenOfModeFeatures = len(self.inputModeNameToFeatures[inputModeName]) 
        #if the array has not been extended to a length that encompasses the index of the id
        if (idIdx >= lenOfModeFeatures):
            #extend it to accomodate the index of the id
            self.inputModeNameToFeatures[inputModeName].extend([None]*(1+(idIdx-lenOfModeFeatures)));
        #check the current contents living at the index of this id for this mode
        currentFeature = self.inputModeNameToFeatures[inputModeName][idIdx] 
        #if it's None, can safely overwrite
        if (currentFeature is None):
            self.inputModeNameToFeatures[inputModeName][idIdx] = featuresForModeAndId
        else: #otherwise, if there was something there
            #if you have disallowed duplicates, then ignore it
            if (duplicatesDisallowed):
                print("I am seeing ",str(theId)," twice for mode "+str(inputModeName)+"! Ignoring...")
            else: #otherwise, attempt to extend the feature array
                self.inputModeNameToFeatures[inputModeName][idIdx].extend(featuresForModeAndId);

def loadTrainTestValidFromYaml(*yamlConfigs):
    import yaml;
    import itertools
    splitNameToInputData = getSplitNameToInputDataFromSeriesOfYamls([yaml.load(fp.getFileHandle(x)) for x in yamlConfigs]);
    trainData = splitNameToInputData['train'];
    validData = splitNameToInputData['valid'];
    testData = splitNameToInputData['test'];
    evalData = splitNameToInputData['eval'];
    print("Making numpy arrays out of the loaded files")
    for dat,setName in zip([trainData, validData, testData], ['train', 'test', 'valid', 'eval']):
        dat.X = np.array(dat.X)
        dat.Y = np.array(dat.Y)
        print(setName, "shape", dat.X.shape)
        print(setName, "shape", dat.Y.shape)
    return trainData, validData, testData, evalData;
