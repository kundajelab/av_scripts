import sys;
import os;
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

def updateLabelRepresentationCountersWithOutcome(labelRepresentationCounters, outcome):
    if len(labelRepresentationCounters) == 0:
        labelRepresentationCounters.extend([LabelRepresentationCounter() for x in outcome]);
    for idx,aClassVal in enumerate(outcome):
        labelRepresentationCounters[idx].update(aClassVal);

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
RootKeys=Keys(Key("features"), Key("labels"), Key("splits"));
FeaturesFormat=util.enum(rowsAndColumns='rowsAndColumns', fasta='fasta', fastaInCol="fastaInCol"); 
FeaturesKeys = Keys(Key("featuresFormat"), Key("opts"));
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
SubsetOfColumnsToUseOptionsYamlKeys = Keys(Key("subsetOfColumnsToUseMode"), Key("fileWithColumnNames",default=None), Key("N", default=None)); 
#subset of cols modes: setOfColumnNames, topN

def getSplitNameToInputDataFromSeriesOfYamls(seriesOfYamls):
    combinedYaml=getCombinedYamlFromSeriesOfYamls(seriesOfYamls);
    return getSplitNameToInputDataFromCombinedYaml(combinedYaml);

def getCombinedYamlFromSeriesOfYamls(seriesOfYamls):
    combinedYaml = OrderedDict([('features',[])]);
    for yamlObject in seriesOfYamls:
        RootKeys.checkForUnsupportedKeys(yamlObject);
        if (RootKeys.keys.features in yamlObject):
            combinedYaml[RootKeys.keys.features].append(yamlObject[RootKeys.keys.features]);
        for key in [RootKeys.keys.labels, RootKeys.keys.splits]:
            if key in yamlObject:
                if key not in combinedYaml:
                    combinedYaml[key] = yamlObject[key];
                else:
                    raise RuntimeError("Two specifications given for "+str(key));
    return combinedYaml;

def getSplitNameToInputDataFromCombinedYaml(combinedYaml):
    idToSplitNames,distinctSplitNames = getIdToSplitNames(combinedYaml[RootKeys.keys.splits]);
    idToLabels, labelNames = getIdToLabels(combinedYaml[RootKeys.keys.labels]);
    splitNameToCompiler = dict((x, DataForSplitCompiler(labelNames)) for x in distinctSplitNames);
    for featuresYamlObject in combinedYaml[RootKeys.keys.features]:
        updateSplitNameToCompilerUsingFeaturesYamlObject(featuresYamlObject, idToSplitNames, idToLabels, splitNameToCompiler);
    print("Returning desired dict");
    toReturn = dict((x,splitNameToCompiler[x].getInputData()) for x in splitNameToCompiler);
    #do a check to see if any of the ids in idToSplitNames were not represented in the final
    #data.
    idsThatDidNotMakeIt = [];
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

#fp.readTitledMapping(fp.getFileHandle(metadataFile), contentType=str, subsetOfColumnsToUseOptions=fp.SubsetOfColumnsToUseOptions(columnNames=relevantColumns))
LabelsKeys = Keys(Key("fileName"), Key("contentType", default=ContentTypes.integer.name), Key("fileWithLabelsToUse",default=None), Key("keyColumns",default=[0]));
def getIdToLabels(labelsObject):
    """
        return:
        idToLabels
        labelNames
    """
    LabelsKeys.fillInDefaultsForKeys(labelsObject);
    LabelsKeys.checkForUnsupportedKeys(labelsObject);
    fileWithLabelsToUse = labelsObject[LabelsKeys.keys.fileWithLabelsToUse];
    titledMapping = fp.readTitledMapping(fp.getFileHandle(labelsObject[LabelsKeys.keys.fileName])
                                            , contentType=getContentTypeFromName(labelsObject[LabelsKeys.keys.contentType])
                                            , keyColumns = labelsObject[LabelsKeys.keys.keyColumns]
                                            , subsetOfColumnsToUseOptions=None if fileWithLabelsToUse is None else fp.SubsetOfColumnsToUseOptions(
                                                    columnNames=fp.readRowsIntoArr(fp.getFileHandle(fileWithLabelsToUse)) 
                                            ));
    return titledMapping.mapping, titledMapping.titleArr;

def getContentTypeFromName(contentTypeName):
    if contentTypeName not in ContentTypesLookup:
        raise RuntimeError("Unsupported content type: "+str(contentTypeName)); 
    return ContentTypesLookup[contentTypeName];

def updateSplitNameToCompilerUsingFeaturesYamlObject(featuresYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
    fileFormat = featuresYamlObject[FeaturesKeys.keys.featuresFormat];
    if (fileFormat == FeaturesFormat.rowsAndColumns):
        updateSplitNameToCompilerUsingFeaturesYamlObject_RowsAndCols(featuresYamlObject[FeaturesKeys.keys.opts], idToSplitNames, idToLabels, splitNameToCompiler);
    elif (fileFormat == FeaturesFormat.fasta):
        updateSplitNameToCompilerUsingFeaturesYamlObject_Fasta(featuresYamlObject[FeaturesKeys.keys.opts], idToSplitNames, idToLabels, splitNameToCompiler);
    elif (fileFormat == FeaturesFormat.fastaInCol):
        updateSplitNameToCompilerUsingFeaturesYamlObject_FastaInCol(featuresYamlObject[FeaturesKeys.keys.opts], idToSplitNames, idToLabels, splitNameToCompiler);
    else:
        raise RuntimeError("Unsupported features file format: "+str(fileFormat));

def featurePreparationActionOnFiles(KeysObj, featureSetYamlObject, featurePreparationActionOnFileHandle):
    for (fileNumber, fileName) in enumerate(featureSetYamlObject[KeysObj.keys.fileNames]):
        skippedFeatureRowsWrapper = util.VariableWrapper(0);
        fileHandle = fp.getFileHandle(fileName);
        featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper);
        print(skippedFeatureRowsWrapper.var,"rows skipped from",fileName); 

def updateSplitNameToCompilerAction(theId, featureProducer, skippedFeatureRowsWrapper, idToSplitNames, idToLabels, splitNameToCompiler):
    if (theId in idToSplitNames):
        for splitName in idToSplitNames[theId]:
            splitNameToCompiler[splitName].update(theId, featureProducer(), outcomesForId=idToLabels[theId]);
    else:
        if (skippedFeatureRowsWrapper.var == 0):
            print("WARNING.",theId,"was not found in train/test/valid splits");
            print("This is the only time such a warning will be printed. Remaining "
                  "such ids will be silently ignored");
        skippedFeatureRowsWrapper.var += 1; 
    
def updateSplitNameToCompilerUsingFeaturesYamlObject_RowsAndCols(featureSetYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
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
                    for splitName in splitNameToCompiler:
                        splitNameToCompiler[splitName].extendPredictorNames(featureNames);
            else:
                #otherwise, just update the predictors.
                theId, features = coreTitledMappingAction(inp, lineNumber);
                updateSplitNameToCompilerAction(theId, lambda: list(features), skippedFeatureRowsWrapper, idToSplitNames, idToLabels, splitNameToCompiler);
        fp.performActionOnEachLineOfFile(
            fileHandle=fileHandle
            ,action=action
            ,transformation=fp.defaultTabSeppd
            ,progressUpdate=featureSetYamlObject[KeysObj.keys.progressUpdate]
        );

    featurePreparationActionOnFiles(KeysObj, featureSetYamlObject, featurePreparationActionOnFileHandle);

def updateSplitNameToCompilerUsingFeaturesYamlObject_Fasta(featureSetYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
    """
        Use the data in a file where the features are fasta rows; the fasta file will be converted to a 2D image.
    """
    KeysObj = FeatureSetYamlKeys_Fasta;
    KeysObj.checkForUnsupportedKeysAndFillInDefaults(featureSetYamlObject)
    def featurePreparationActionOnFileHandle(fileNumber, fileName, fileHandle, skippedFeatureRowsWrapper):
        fastaIterator = fp.FastaIterator(fileHandle, progressUpdate=featureSetYamlObject[KeysObj.keys.progressUpdate], progressUpdateFileName=fileName);
        for (seqNumber, (seqName, seq)) in enumerate(fastaIterator):
            #in the case of this dataset, I'm not going to try to update predictorNames as it's going to be the 2D image thing.
            updateSplitNameToCompilerAction(seqName, lambda: util.seqTo2Dimage(seq), skippedFeatureRowsWrapper, idToSplitNames, idToLabels, splitNameToCompiler);
    featurePreparationActionOnFiles(KeysObj, featureSetYamlObject, featurePreparationActionOnFileHandle);
    print("Done loading in fastas");

def updateSplitNameToCompilerUsingFeaturesYamlObject_FastaInCol(featureSetYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
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
            updateSplitNameToCompilerAction(seqName, lambda: util.seqTo2Dimage(seq), skippedFeatureRowsWrapper, idToSplitNames, idToLabels, splitNameToCompiler);
        fp.performActionOnEachLineOfFile(fileHandle = fileHandle
                                        , action=action, transformation=fp.defaultTabSeppd
                                        , progressUpdateFileName=featureSetYamlObject[KeysObj.keys.progressUpdate]
                                        , ignoreInputTitle=featureSetYamlObject[KeysObj.keys.titlePresent]);
    featurePreparationActionOnFiles(KeysObj, featureSetYamlObject, featurePreparationActionOnFileHandle);

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
    def __init__(self, ids, X, Y, featureNames, labelNames, labelRepresentationCounters):
        self.ids = ids;
        self.X = X;
        self.Y = Y;
        self.featureNames = featureNames;
        self.labelNames = labelNames;
        self.labelRepresentationCounters = labelRepresentationCounters;
    @staticmethod
    def concat(*inputDatas):
        ids = [y for inputData in inputDatas for y in inputData.ids];
        X = np.concatenate([inputData.X for inputData in inputDatas], axis=0);
        Y = np.concatenate([inputData.Y for inputData in inputDatas], axis=0);
        featureNames = inputDatas[0].featureNames;
        labelNames = inputDatas[0].labelNames
        print("Punting on deadling with concat for labelRepresentationCounters for now");
        return InputData(ids=ids, X=X, Y=Y
                        , featureNames=featureNames
                        , labelNames=labelNames
                        , labelRepresentationCounters=None);

class DataForSplitCompiler(object):
    """
        Compiles the data for a particular train/test/valid split; data is added via the update call
        At the end, call getInputData to finalise.
    """    
    def __init__(self, outcomesNames=None):
        self.ids = [];
        self.idToIndex = {};
        self.outcomesNames=outcomesNames; #mostly relevant for multilabel case
        self.predictorNames=[]; #depending on the dataset, this may be left empty.
        self.outcomes=[];
        self.predictors=[];
        self.labelRepresentationCounters=[];
    def extendPredictorNames(self, newPredictorNames):
        self.predictorNames.extend(newPredictorNames);
    def getInputData(self):
        for outcome in self.outcomes:
            pass;
            #TODO: handle multiclass labels; no longer just ones and zeros...
            #updateLabelRepresentationCountersWithOutcome(self.labelRepresentationCounters, outcome);
        for labelRepresentationCounter in self.labelRepresentationCounters:
            labelRepresentationCounter.finalise();
        return InputData(self.ids, self.predictors, self.outcomes, self.predictorNames, self.outcomesNames, self.labelRepresentationCounters);
    def update(self, theId, predictorsForId, outcomesForId=None, duplicatesDisallowed=False):
            if (theId not in self.idToIndex):
                self.idToIndex[theId] = len(self.ids);
                self.ids.append(theId)
                self.outcomes.append(outcomesForId);
                self.predictors.append(predictorsForId) 
            else:
                if (duplicatesDisallowed):
                    print("I am seeing ",str(theId)," twice! Ignoring...")
                else:
                    self.extendFeatures(theId, predictorsForId);
    def extendFeatures(self, theId, additionalFeatures):
        """
            pulls up the features column for theId and extends it by additionalFeatures.
        """
        self.predictors[self.idToIndex[theId]].extend(additionalFeatures);

def loadTrainTestValidFromYaml(*yamlConfigs):
    import yaml;
    splitNameToInputData = getSplitNameToInputDataFromSeriesOfYamls(
                            [yaml.load(fp.getFileHandle(x)) for x in yamlConfigs]);
    trainData = splitNameToInputData['train'];
    validData = splitNameToInputData['valid'];
    testData = splitNameToInputData['test'];
    print("Making numpy arrays out of the loaded files")
    for dat,setName in zip([trainData, validData, testData], ['train', 'test', 'valid']):
        dat.X = np.array(dat.X)
        dat.Y = np.array(dat.Y)
        print(setName, "shape", dat.X.shape)
        print(setName, "shape", dat.Y.shape)
    return trainData, validData, testData;
