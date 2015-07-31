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
from misc import LabelRepresentationCounter;
from misc import loadMultiLabelLookup;
from collections import namedtuple;
from collections import OrderedDict;

ClassificationType = util.enum(
    multiclass="multiclass"
    ,multilabel="multilabel"
    , multitaskMultilabel_firstTaskPosOrNot="multitaskMultilabel_firstTaskPosOrNot");

INPUT_INDEX_NAMES = util.enum(idCol='idCol', dataStartCol='1');
INPUT_INDEX_DEFAULTS = {INPUT_INDEX_NAMES.idCol:0, INPUT_INDEX_NAMES.dataStartCol:1};

class ClassificationOptions(object):
    def __init__(self, classificationType):
        """
            classificationType: one of ClassificationType
        """
        self._classificationType = classificationType;
    def getClassificationType(self):
        return self._classificationType;

class InputData(object):
    """
        This class represents all the input data for a particular split.
    """
    def __init__(self, ids, X, Y, labelRepresentationCounters):
        """
            ids: array of string is
            X, Y: numpy arrays
            labelRepresentationCounters: array of misc.LabelRepresentationCounters (one per column of Y, I believe) 
        """
        self.ids = ids;
        self.X = X;
        self.Y = Y;
        self.labelRepresentationCounters = labelRepresentationCounters;
    def concatenate(self, inputData):
        if (self.labelRepresentationCounters is not None):
            self.mergeLabelRepresentationCounters(inputData.labelRepresentationCounters)
        return InputData(self.ids+inputData.ids,
                        , np.concatenate((self.X,inputData.X),axis=0)
                        , np.concatenate((self.Y, inputData.Y),axis=0)
                        , self.labelRepresentationCounters);
    def mergeLabelRepresentationCounters(self, labelRepresentationCounters):
        assert labelRepresentationCounters is not None;
        if self.labelRepresentationCounters is None:
            self.labelRepresentationCounters = labelRepresentationCounters;
        else:
            #merge the labelRepresentation counts.
            for idx in range(len(self.labelRepresentationCounters)):
                self.labelRepresentationCounters[idx] = self.labelRepresentationCounters[idx].merge(labelRepresentationCounters[idx]);

class DynamicEnum(object):
    """
        just a wrapper around a dictionary, so that the keys are
        accessible using the object attribute syntax rather
        than the dictionary syntax.
    """
    def __init__(self):
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
class Key(object)
    def __init__(self, keyNameInternal, keyNameExternal=None, default=UNDEF):
        self.keyNameInternal = keyNameInternal;
        if (self.keyNameExternal is None):
            self.keyNameExternal = keyNameInternal;
        self.default=default;
def Keys(object):
    def __init__(self, keys*):
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
                if (hasKey(self.keysDefaults, aKey)==False):
                    raise RuntimeError("Default for "+str(aKey)+" not present, and a value was not provided");
                aDict[aKey] = self.keysDefaults.getKey(aKey);

ContentType=namedtuple('ContentType',['name','castingFunction']);
ContentTypes=util.enum(integer=ContentType("int",int),floating=ContentType("float",float),string=ContentType("str",str));
FeatureSetYamlKeys_RowsAndCols = Keys(Key("fileName")
                            ,Key("contentType",default=ContenTypes.integer.name)
                            ,Key("contentStartIndex",default=1)
                            ,Key("fileWithSubsetOfColumnsToUse",default=None)
                            ,Key("fileWithSubsetOfRowsToUse",default=None)
                            ,Key("progressUpdate",default=None));

def createFeatureSetFromYamlObject_RowsAndCols(featureSetYamlObject):
    FeatureSetYamlKeys_RowsAndCols.checkForUnsupportedKeys(featureSetYamlObject); 
    FeatureSetYamlKeys_RowsAndCols.fillInDefaultsForKeys(featureSetYamlObject);

#######MARKER


def load_data_action(fileHandle, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPreppers, dataPrepper, indexSettings, featureSubset=None, topNFeatures=None): 
    """
        reads in the rows from fileHandle, which is the feature file. extracts the id according to indexSettings, and the features according
        to indexSettings or featureSubset. If applicable, does a lookup of the id in yLookup and only proceeds if a hit is found. Checks for the
        id in dataSplitToDataPreppers (if applicable) and passes the id to the appropriate dataPrepper instance(s). Note that the DataPrepper class is at the time
        of writing only set up to include multiLabel hits that are active in at least one label.

        classificationOption is one of DATASET_OPTS
        
        Only one of dataSplitToDataPreppers or dataPrepper should be set.

        dataSplitToDataPreppers is specified, just updates the dataPrepper for each split. Otherwise, just update dataPrepper.

        I expect myself to deprecate the interface that doesn't use dataSplitToDataPreppers later on. 
    """
    assert featureSubset is None or topNFeatures is None; #both cannot be non-None as they would conflict. 
    assert dataSplitToDataPreppers is None or dataPrepper is None;
    assert dataSplitToDataPreppers is not None or dataPrepper is not None;
    if (classificationOption in [DATASET_OPTS.ENH_AND_TISSUE_BASED_CLASSIFICATION, DATASET_OPTS.ONLY_TISSUE_BASED_CLASSIFICATION]):
        if multiLabelLookup is None:
            raise RuntimeError("multiLabelLookup should be set if classification option is "+classificationOption);
    featureSubsetIndices = []
    #action to be performed on each line of the file
    def action(row,lineNumber):
        if (lineNumber == 1):
            if (featureSubset is not None):
                assert topNFeatures is None;
                featureSubsetDict = dict((x,1) for x in featureSubset);
                for (i, name) in enumerate(row):
                    if name in featureSubsetDict:
                        featureSubsetIndices.append(i);
                        del featureSubsetDict[name];
                assert len(featureSubsetDict.keys()) == 0; 
            if (topNFeatures is not None):
                assert featureSubset is None;
                featureSubsetIndices.extend([x+indexSettings[INPUT_INDEX_NAMES.dataStartCol] for x in range(topNFeatures)]);
        else:
            theId = row[indexSettings[INPUT_INDEX_NAMES.idCol]];
            if (classificationOption in [DATASET_OPTS.OUTPUT_IS_ABSENT, DATASET_OPTS.ONLY_TISSUE_BASED_CLASSIFICATION]):
                isEnhancer = None;
                theCategory = None;
                if (classificationOption==DATASET_OPTS.ONLY_TISSUE_BASED_CLASSIFICATION):
                    assert multiLabelLookup is not None;
            else: #if above condition is not met, then isEnhancer/theCategory should be specified either in yLookup
                assert yLookup is not None;
                isEnhancer = yLookup.getLabel(theId);
                theCategory = yLookup.getCategory(theId);
            if (yLookup is not None and theId in yLookup.idToYLookupEntry) or (multiLabelLookup is not None and theId in multiLabelLookup.lookupDict) or (classificationOption==DATASET_OPTS.OUTPUT_IS_ABSENT):
                if dataSplitToDataPreppers is not None:
                    processedRow = None;
                    for dataSplit in dataSplitToDataPreppers:
                        if theId in dataSplit.theSet:
                            if processedRow is None: #we only want to process a row once even if it appears in multiple splits
                                processedRow = processRow(row, indexSettings, yLookup, featureSubsetIndices);
                            dataSplitToDataPreppers[dataSplit].update(theId, isEnhancer, theCategory, processedRow);
                else:
                    processedRow = processRow(row, indexSettings, yLookup, featureSubsetIndices);
                    dataPrepper.update(theId, isEnhancer, theCategory, processedRow);
    return action

def processRow(row, indexSettings, yLookup, featureSubsetIndices):
    if (featureSubsetIndices is None or len(featureSubsetIndices) == 0):
        processedRow = row[indexSettings[INPUT_INDEX_NAMES.dataStartCol]:]
    else:
        processedRow = [row[i] for i in featureSubsetIndices];
    return processedRow;

class DataPrepper(object):
    """
        Maintains the data for a particular train/test/valid split; data is added via the update call
    """    
    def __init__(self, classificationOption, multiLabelLookup=None):
        self.classificationOption = classificationOption;
        self.multiLabelLookup = multiLabelLookup;
        self.ids = [];
        self.categories=[];
        self.outcomes=[];
        self.predictors=[];
        self.labelRepresentationCounters=[];
    def getInputData(self):
        for labelRepresentationCounter in self.labelRepresentationCounters:
            labelRepresentationCounter.finalise();
        return InputData(self.ids, np.array(self.predictors), np.array(self.outcomes), self.labelRepresentationCounters);
    def update(self, theId, isEnhancer, theCategory, row):
        """
            theId: id of the region
            isEnhancer: necessary for binary classification; 1 or 0
            theCategory: used for multi-class classification; value here will be mapped to a class
            row: the feature row.
        """
        outcomeToAppend = None; #if this stays as none, won't be included unless classification option is set to OUTPUT_IS_ABSENT
        #if are using a yLookup and theId was not present for the yLookup,
        #isEnhancer will be None
        if isEnhancer is not None or theCategory is not None:
            if (self.classificationOption!=DATASET_OPTS.OUTPUT_IS_ABSENT):
                if (self.classificationOption == DATASET_OPTS.CLUSTER_BASED_CLASSIFICATION):
                    outcomeToAppend = clusterToSoftmaxClass(theCategory);
                elif (self.classificationOption == DATASET_OPTS.JISRAELI_STATES):
                    outcomeToAppend = multiclassNumberToSoftmaxClass(8,theCategory);
                elif (self.classificationOption == DATASET_OPTS.YIFENG3):
                    outcomeToAppend = multiclassNumberToSoftmaxClass(3,theCategory);
                elif (self.classificationOption == DATASET_OPTS.ENHANCER_VS_NOT_ENHANCER):
                    outcomeToAppend = [1,0] if isEnhancer == 0 else [0,1];
                elif (self.classificationOption in [DATASET_OPTS.ENH_AND_TISSUE_BASED_CLASSIFICATION]):
                    outcomeToAppend = (multiLabelLookup.lookupDict[theId]) if (isEnhancer==1)\
                                else ([0]*len(multiLabelLookup.labelOrdering)) #recall that the first label is 'isEnhancer'
                else:
                    raise ValueError("Unrecognised classification option: "+self.classificationOption);
        elif (self.classificationOption in [DATASET_OPTS.ONLY_TISSUE_BASED_CLASSIFICATION]): 
            assert theId in self.multiLabelLookup.lookupDict;
            outcomeToAppend_tentative = self.multiLabelLookup.lookupDict[theId]
            if (sum(outcomeToAppend_tentative) > 0): #we only include those for which there is activity in SOME tissue
                outcomeToAppend = outcomeToAppend_tentative #otherwise it stays as None
        else:
            raise ValueError("Either classification option should be multilabel (called ONLY_TISSUE_BASED_CLASSIFICATION), or one of isEnhancer/theCategory should be specified");
         
        #outcomeToAppend is None if didn't find a fit in the multilable lookup or in the yLookup 
        if outcomeToAppend is not None or self.classificationOption==DATASET_OPTS.OUTPUT_IS_ABSENT:
            #TODO: create a map from the id to the index
            self.ids.append(theId)
            self.categories.append(None if self.classificationOption==DATASET_OPTS.OUTPUT_IS_ABSENT else theCategory)
            self.outcomes.append(None if self.classificationOption==DATASET_OPTS.OUTPUT_IS_ABSENT else outcomeToAppend);
            if (self.classificationOption!=DATASET_OPTS.OUTPUT_IS_ABSENT):
                #keep track of how biased your classes are:
                updateLabelRepresentationCountersWithOutcome(self.labelRepresentationCounters, self.outcomes[-1]);
            #the input data used to predict the classes:
            try: ##TODO: make option; exception catching is inefficient
                self.predictors.append([int(base) for base in row])
            except:
                self.predictors.append([float(base) for base in row])        
    def extendFeatures(self, theId, additionalFeatures):
        """
            pulls up the features column for theId and extends it by additionalFeatures.
            ...if the features are not present, should come up with some dummy features??? --> deal with later
        """
        raise NotImplementedError();

class YLookupEntry(object):
    def __init__(self, label, category=None):
        self.label = label;
        self.category = category;

class YLookup(object):
    def __init__(self, idToYLookupEntry):
        self.idToYLookupEntry = idToYLookupEntry;
        print(len(idToYLookupEntry.keys()));
    def getLabel(self, theId):
        return self.idToYLookupEntry[theId].label if theId in self.idToYLookupEntry else None;
    def getCategory(self, theId):
        return self.idToYLookupEntry[theId].category if theId in self.idToYLookupEntry else None;

def readYLookupFile(fileHandle, idIndex=0, labelIndex=1, categoryIndex=2, labelIsFloat=False):
    idToYLookupEntry = {};
    def action(inp, lineNumber):
        theId = inp[idIndex];
        if theId != "id": #if is not a title row...
            theId = inp[idIndex];
            label = int(inp[labelIndex]) if not labelIsFloat else float(inp[labelIndex]);
            category = label if categoryIndex is None else inp[categoryIndex];
            idToYLookupEntry[theId] = YLookupEntry(label, category);
    fp.performActionOnEachLineOfFile(
        fileHandle
        ,action=action
        ,transformation=fp.defaultTabSeppd
    );
    yLookup = YLookup(idToYLookupEntry);
    return yLookup;

def updateLabelRepresentationCountersWithOutcome(labelRepresentationCounters, outcome):
    if len(labelRepresentationCounters) == 0:
        labelRepresentationCounters.extend([LabelRepresentationCounter() for x in outcome]);
    for idx,aClassVal in enumerate(outcome):
        labelRepresentationCounters[idx].update(aClassVal);

def load_data_single_filehandle(data_path_file_handle, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPrepper, dataPrepper, indexSettings, featureSubset=None, topNFeatures=None):
    """
        Fills the dataSplitToDataPrepper object with data
    """
    assert featureSubset is None or topNFeatures is None; #at least one of them should be None
    assert dataSplitToDataPrepper is None or dataPrepper is None;
    assert dataSplitToDataPrepper is not None or dataPrepper is not None;
    action = load_data_action(data_path_file_handle, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPrepper, dataPrepper, indexSettings=indexSettings, featureSubset=featureSubset, topNFeatures=topNFeatures);
    fp.performActionOnEachLineOfFile(
        data_path_file_handle
        , transformation = fp.defaultTabSeppd
        , action=action
        , progressUpdate = 100000
    );

def readFeatureSubset(featureSubsetFile, topNFeatures=None):
    featureSubset = [];
    if (topNFeatures is not None):
        print("Considering only first",topNFeatures,"features of the feature subset file");
    def action(inp, lineNumber):
        if (topNFeatures == None or lineNumber <= topNFeatures):
            featureSubset.append(inp[0]);
    fp.performActionOnEachLineOfFile(
        fileHandle = fp.getFileHandle(featureSubsetFile)
        , transformation=fp.defaultTabSeppd
        , action = action
    );
    return featureSubset; 

def load_data_multipleFiles(data_paths, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPrepper, indexSettings, dataPrepper=None, featureSubsetFile=None, topNFeatures=None):
    assert dataSplitToDataPrepper is None or dataPrepper is None;
    assert dataSplitToDataPrepper is not None or dataPrepper is not None;
    if (featureSubsetFile is not None):
        featureSubset = readFeatureSubset(featureSubsetFile, topNFeatures=topNFeatures);
        topNFeatures=None; #the information on topNFeatures has been incorporated into featureSubset. If featureSubset is None, topNFeatures is interpreted as topN in the input data
    else:
        featureSubset = None;
    for data_path in data_paths:
        print "reading: "+data_path;
        fileHandle = fp.getFileHandle(data_path);
        load_data_single_filehandle(fileHandle, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPrepper, dataPrepper, indexSettings, featureSubset, topNFeatures);  

def load_data_multipleFiles_multipleSplits(data_paths, classificationOption, multiLabelLookup, yLookup, splitNameToSplit, indexSettings, featureSubsetFile=None, topNFeatures=None, minMaxScale=False):
    """
        returns datasetNameToData, 
    """
    dataSplitToDataPrepper = dict((splitNameToSplit[x], DataPrepper(classificationOption, multiLabelLookup)) for x in splitNameToSplit);
    load_data_multipleFiles(data_paths, classificationOption, multiLabelLookup, yLookup, dataSplitToDataPrepper, indexSettings, featureSubsetFile=featureSubsetFile, topNFeatures=topNFeatures);
    datasetNameToData = dict((x, dataSplitToDataPrepper[splitNameToSplit[x]].getInputData()) for x in splitNameToSplit);
    if (minMaxScale): 
        minMaxScaler = preprocessing.MinMaxScaler();
        minMaxScaler.fit(datasetNameToData['train'].X);
        for data in datasetNameToData.values():
            data.X = minMaxScaler.transform(data.X);
    return datasetNameToData;

class DataSplit(object):
    def __init__(self, dataSplitName, theFile, col=0, titlePresent=False):
        self.dataSplitName = dataSplitName;
        self.theSet = Set(fp.readColIntoArr(fp.getFileHandle(theFile), col=col, titlePresent=titlePresent));

def getDatasetNameToDataSplit(splitNameToSplitFiles, **kwargs):
    print "splits",splitNameToSplitFiles;
    return dict((x, DataSplit(x, splitNameToSplitFiles[x], **kwargs)) for x in splitNameToSplitFiles);     

YAML_KEYS = util.enum(
    inputFeatures="inputFeatures" #map to a dictionary with keys "YAML_INPUT_FEATURES_KEYS"
    , yLookup="yLookup" #for classification, a place to lookup the value of y; maps to a dictionary with keys YAML_YLOOKUP_KEYS
    , classificationOption="classificationOption" #one of DATASET_OPTS
    , multiLabelLookup="multiLabelLookup" #can specify instead of yLookup if doing multiLabel. Current setup is such that only columns with at least one 1 will be loaded. Maps toa  dictionary with keys YAML_MULTILABEL_KEYS
    , split="split" #train/test/validation splits; only the IDs specified here will be loaded. Maps to an object with keys YAML_SPLIT_KEYS
    ); 

YAML_INPUTFEATURES_KEYS = util.enum(
    dataPaths="dataPaths" #paths to the files with the features
    , indexSettings="indexSettings" #optional; if ID is not in col 0 or features don't start from col 1 (and you haven't specified a feature subset), should indicate here to override the defaults; defaults in INPUT_INDEX_DEFAULTS, and possible keys in INPUT_INDEX_NAMES;
    , featureSubsetFile='featureSubsetFile' #in case you only want to load a subset of the columns in your feature file.
    , topNFeatures = 'topNFeatures' #if featureSubsetFile specified, picks top N cols from it. Otherwise picks first N cols in input feature file.
);
YAML_YLOOKUP_KEYS = util.enum(yLookupFile="yLookupFile", idIndex="idIndex", labelIndex="labelIndex", categoryIndex="categoryIndex");
YAML_MULTILABEL_KEYS = util.enum(lookupFile="lookupFile", chosenTissuesFile="chosenTissuesFile"); 
YAML_SPLIT_KEYS = util.enum(splitNameToSplitFiles="splitNameToSplitFiles", opts="opts");
YAML_SPLIT_KEYS_OPTS = util.enum(titlePresent="titlePresent", col="col");

def getSplitInfoFromYaml(yamlInfo):
    kwargs = {};
    opts = yamlInfo[YAML_SPLIT_KEYS.opts];
    for opt in YAML_SPLIT_KEYS_OPTS.vals:
        if opt in opts:
            kwargs[opt] = opts[opt];
    splitNameToSplit = None if YAML_SPLIT_KEYS.splitNameToSplitFiles not in yamlInfo else getDatasetNameToDataSplit(yamlInfo[YAML_SPLIT_KEYS.splitNameToSplitFiles], **kwargs);
    return splitNameToSplit;  
    
def getYLookupFromYaml(yamlInfo):
    yLookupFile = yamlInfo[YAML_YLOOKUP_KEYS.yLookupFile];
    kwargs = {};
    for kwarg in [YAML_YLOOKUP_KEYS.idIndex, YAML_YLOOKUP_KEYS.labelIndex, YAML_YLOOKUP_KEYS.categoryIndex]:
        if kwarg in yamlInfo:
            kwargs[kwarg] = yamlInfo[kwarg];
    return readYLookupFile(fp.getFileHandle(yLookupFile), **kwargs);

def getMultiLabelInfoFromYaml(yamlInfo, classificationOption):
    lookupFile = yamlInfo[YAML_MULTILABEL_KEYS.lookupFile];
    if YAML_MULTILABEL_KEYS.chosenTissuesFile not in yamlInfo:
        chosenTissues = None;
    else:
        chosenTissues = fp.readRowsIntoArr(yamlInfo[YAML_MULTILABEL_KEYS.chosenTissuesFile]);
    multilabelLookup = loadMultiLabelLookup(lookupFile, classificationOption, chosenTissues);
    return multilabelLookup;

AllLoadedData = namedtuple('YamlConfig', ['multiLabelLookup', 'classificationOption','datasetNameToData']);
def load_data_from_yaml_configs(pathsToYaml):
    parsedYaml = util.parseMultipleYamlFiles(pathsToYaml);
    assert YAML_KEYS.dataPaths in parsedYaml;
    assert YAML_KEYS.classificationOption in parsedYaml;
    return load_data_from_parsed_yaml_configs(parsedYaml);

def load_data_from_parsed_yaml_configs(parsedOptionsDict):
    print("Parsed options dict:");
    print(parsedOptionsDict);
    dataPaths = parsedOptionsDict[YAML_KEYS.dataPaths];
    indexSettings = INPUT_INDEX_DEFAULTS;
    if YAML_KEYS.indexSettings in parsedOptionsDict:
        overrideIndexSettings = parsedOptionsDict[YAML_KEYS.indexSettings];
        for key in overrideIndexSettings:
            if key not in indexSettings:
                raise RuntimeError(key+" is not a recognised index key; recognised keys are: "+str(indexSettings.keys()));
            else:
                indexSettings[key] = overrideIndexSettings[key];
    classificationOption = parsedOptionsDict[YAML_KEYS.classificationOption];
    assert classificationOption in DATASET_OPTS.vals;
    yLookup = None if YAML_KEYS.yLookup not in parsedOptionsDict else getYLookupFromYaml(parsedOptionsDict[YAML_KEYS.yLookup]);
    featureSubsetFile = None if YAML_KEYS.featureSubsetFile not in parsedOptionsDict else parsedOptionsDict[YAML_KEYS.featureSubsetFile];
    topNFeatures = None if YAML_KEYS.topNFeatures not in parsedOptionsDict else parsedOptionsDict[YAML_KEYS.topNFeatures];
    splitNameToSplit = getSplitInfoFromYaml(parsedOptionsDict[YAML_KEYS.split]);
    multiLabelLookup = None if YAML_KEYS.multiLabelLookup not in parsedOptionsDict else getMultiLabelInfoFromYaml(parsedOptionsDict[YAML_KEYS.multiLabelLookup], classificationOption);   
    return AllLoadedData(multiLabelLookup, classificationOption, load_data_multipleFiles_multipleSplits(dataPaths, classificationOption, multiLabelLookup, yLookup, splitNameToSplit, indexSettings=indexSettings, featureSubsetFile=featureSubsetFile, topNFeatures=topNFeatures));
    

def clusterToSoftmaxClass(x):
    numClasses = 62;
    cluster = int(x.split("_")[-1]) if "cluster" in x else None;
    background = 1 if ("random" in x or "shuffled" in x) else 0;
    toReturn = [0]*(numClasses+1);
    index = 0 if background else cluster;
    if (index >= len(toReturn)):
        print "toReturn: "+str(len(toReturn));
        print "cluster: "+str(cluster);
        print "x: "+x;
        print "shuffled: "+str(shuffled);
        print "index: "+str(index);
    toReturn[index] = 1;
    return toReturn;

def jisraeliStateToSoftmaxClass(x):
    return multiclassNumberToSoftmaxClass(8,x);

def yifeng3ToSoftmaxClass(x):
    return multiclassNumberToSoftmaxClass(3,x);

def multiclassNumberToSoftmaxClass(numClasses, x):
    index = int(x);
    toReturn = [0]*(numClasses);
    if (index >= len(toReturn)):
        print "toReturn: "+str(len(toReturn));
        print "index: "+str(index);
        raise RuntimeError();
    toReturn[index] = 1;
    return toReturn;

##Need to figure out how to configure for multiple yLookups
def load_data_iter(data_path, classificationOption, multiLabelLookup, loadingChunk):
    """
        This is used by pytables to read from the file in batches.
        I am leaving it in here because it uses the signature for load_data_action,
        so if I update that signature I want to make sure I remember to update this.
    """
    print "on: "+str(data_path);
    fileHandle = fp.getFileHandle(data_path);
    dataPrepper = util.VariableWrapper(None);
 
    lineNumber = 0;
    fileHandle.readline(); #discard input title;
    for rawinp in fileHandle:
        inp = fp.trimNewline(rawinp);
        inp = fp.splitByTabs(inp);
        lineNumber += 1; 
        if (lineNumber%loadingChunk == 0 or lineNumber == 1):
            if lineNumber > 1 and len(ids) > 0:
                yield dataPrepper.var.ids,dataPrepper.var.categories,dataPrepper.var.outcomes,dataPrepper.var.predictors,dataPrepper.var.labelRepresentationCounters;
            dataPrepper.var = DataPrepper();
            action = load_data_action(fileHandle
                                        , classificationOption=classificationOption
                                        , multiLabelLookup = multiLabelLookup
                                        , yLookupToDataPreppers=None
                                        , dataPrepper=dataPrepper.var); 
        action(inp,lineNumber);
        if (lineNumber % 10000 == 0):
            print "processed "+str(lineNumber);
    if (len(idsWrapper.var) > 0):
        yield dataPrepper.var.ids,dataPrepper.var.categories,dataPrepper.var.outcomes,dataPrepper.var.predictors,dataPrepper.var.labelRepresentationCounters;
