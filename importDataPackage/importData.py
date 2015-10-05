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

#something like pytable is sufficiently different that
#we can assume all this loading is for in-memory situations
ContentType=namedtuple('ContentType',['name','castingFunction']);
ContentTypes=util.enum(integer=ContentType("int",int),floating=ContentType("float",float),string=ContentType("str",str));
ContentTypesLookup = dict((x.name,x.castingFunction) for x in ContentTypes.vals);
RootKeys=Keys(Key("features"), Key("labels"), Key("splits"));
FeaturesFormat=util.enum(rowsAndColumns='rowsAndColumns', fasta='fasta'); 
FeaturesKeys = Keys(Key("featuresFormat"), Key("opts"));
FeatureSetYamlKeys_RowsAndCols = Keys(
                            Key("fileNames")
                            ,Key("contentType",default=ContentTypes.floating.name)
                            ,Key("contentStartIndex",default=1)
                            ,Key("subsetOfColumnsToUseOptions",default=None)
                            ,Key("progressUpdate",default=None));
FeatureSetYamlKeys_Fasta = Keys(Key("fileNames"), Key("progressUpdate",default=None));
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
    return dict((x,splitNameToCompiler[x].getInputData()) for x in splitNameToCompiler);

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
LabelsKeys = Keys(Key("fileName"), Key("contentType", default=ContentTypes.integer.name), Key("fileWithLabelsToUse",default=None));
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
    else:
        raise RuntimeError("Unsupported features file format: "+str(fileFormat));

def updateSplitNameToCompilerUsingFeaturesYamlObject_RowsAndCols(featureSetYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
    """
        Use the data in a file where the features are stored as rows and columns to update the splits.
    """
    FeatureSetYamlKeys_RowsAndCols.checkForUnsupportedKeys(featureSetYamlObject); 
    FeatureSetYamlKeys_RowsAndCols.fillInDefaultsForKeys(featureSetYamlObject);
    subsetOfColumnsToUseOptions = (None if featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.subsetOfColumnsToUseOptions] is None
                                    else createSubsetOfColumnsToUseOptionsFromYamlObject(
                                            featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.subsetOfColumnsToUseOptions])); 
    contentType = getContentTypeFromName(featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.contentType]);
    contentStartIndex = featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.contentStartIndex];
    for (fileNumber,fileName) in enumerate(featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.fileNames]):
        skippedFeatureRows = util.VariableWrapper(0);
        fileHandle = fp.getFileHandle(fileName);
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
                if (theId in idToSplitNames): #only consider id's in splits
                    for splitName in idToSplitNames[theId]:
                        splitNameToCompiler[splitName].update(theId, features, outcomesForId=idToLabels[theId]);
                else:
                    skippedFeatureRows.var += 1;
        fp.performActionOnEachLineOfFile(
            fileHandle=fileHandle
            ,action=action
            ,transformation=fp.defaultTabSeppd
            ,progressUpdate=featureSetYamlObject[FeatureSetYamlKeys_RowsAndCols.keys.progressUpdate]
        );
        print(skippedFeatureRows.var,"rows skipped from",fileName); 

def updateSplitNameToCompilerUsingFeaturesYamlObject_Fasta(featureSetYamlObject, idToSplitNames, idToLabels, splitNameToCompiler):
    """
        Use the data in a file where the features are fasta rows; the fasta file will be converted to a 2D image.
    """
    FeatureSetYamlKeys_Fasta.checkForUnsupportedKeys(featureSetYamlObject); 
    FeatureSetYamlKeys_Fasta.fillInDefaultsForKeys(featureSetYamlObject);
    for (fileNumber,fileName) in enumerate(featureSetYamlObject[FeatureSetYamlKeys_Fasta.keys.fileNames]):
        skippedFeatureRows=0;
        fileHandle = fp.getFileHandle(fileName);
        fastaIterator = fp.FastaIterator(fileHandle, progressUpdate=featureSetYamlObject[FeatureSetYamlKeys_Fasta.keys.progressUpdate], progressUpdateFileName=fileName);
        for (seqNumber, (seqName, seq)) in enumerate(fastaIterator):
            #in the case of this dataset, I'm not going to try to update predictorNames as it's going to be the 2D image thing.
            the2DimageOfSeq = util.seqTo2Dimage(seq);
            if (seqName in idToSplitNames): #only consider id's in splits
                for splitName in idToSplitNames[seqName]:
                    splitNameToCompiler[splitName].update(seqName, the2DimageOfSeq, outcomesForId=idToLabels[seqName]); 
            else:
                skippedFeatureRows+=1;
        print(skippedFeatureRows,"rows skipped from",fileName); 

SubsetOfColumnsToUseOptionsYamlKeys = Keys(Key("subsetOfColumnsToUseMode"), Key("fileWithColumnNames",default=None), Key("N", default=None)); 
def createSubsetOfColumnsToUseOptionsFromYamlObject(subsetOfColumnsToUseYamlObject):
    """
        create fp.SubsetOfColumnsToUseOptions object from yaml devoted to it
    """
    SubsetOfColumnsToUseOptionsYamlKeys.fillInDefaultsForKeys(subsetOfColumnsToUseYamlObject);
    SubsetOfColumnsToUseOptionsYamlKeys.checkForUnsupportedKeys(subsetOfColumnsToUseYamlObject); 
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
        return InputData(self.ids, np.array(self.predictors), np.array(self.outcomes), self.predictorNames, self.outcomesNames, self.labelRepresentationCounters);
    def update(self, theId, predictorsForId, outcomesForId=None):
            if (theId not in self.idToIndex):
                self.idToIndex[theId] = len(self.ids);
                self.ids.append(theId)
                self.outcomes.append(outcomesForId);
                self.predictors.append(list(predictorsForId)) #make a copy so that doesn't get double-added to when same id appears in multiple splits
            else:
                self.extendFeatures(theId, predictorsForId);
    def extendFeatures(self, theId, additionalFeatures):
        """
            pulls up the features column for theId and extends it by additionalFeatures.
        """
        self.predictors[self.idToIndex[theId]].extend(additionalFeatures);



