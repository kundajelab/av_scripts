#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import abc;
from collections import namedtuple

JsonDb = namedtuple("JsonDb", ["metadata", "jsonableRecords"]);

class AbstractMetadataClass(object):
    __metaclass__ = abc.ABCMeta 
    @abc.abstractmethod
    def updateForRecord(self, record):
        raise NotImplementedError();
    @abc.abstractmethod
    def getJsonableObject(self):
        raise NotImplementedError();
    @classmethod
    def constructFromJson(cls, json):
        return cls(**json); 
    @classmethod
    def defaultInit(cls):
        return cls();

MetadataUpdateInfo = namedtuple("MetadataUpdateInfo", ["valName", "updateFunc"]);
def getUpdateValsMetadataClass(metadataUpdateInfos):
    """
        A metadata class that updates some values based on
            the records added
    """
    metadataValNameToMetadataInfoLookup = OrderedDict([(x.valName, x) for x in metadataUpdateInfos]);
    class UpdateValsMetadataClass(AbstractMetadataClass):
        metadataValNameToMetadataInfoLookup = metadataUpdateInfos;
        metadataUpdateInfos = metadataUpdateInfos; 
        def __init__(self, **kwargs):
            for kwarg in kwargs:
                if kwarg not in self.metadataValNameToMetadataInfoLookup:
                    raise RuntimeError(kwarg+" not in lookups"); 
            self.__dict__.update(kwargs);
        def updateForRecord(self, record):
            for metadataUpdateInfo in self.metadataUpdateInfos:
                valName = metadataUpdateInfo.valName;
                recordVal = getattr(record, valName);
                selfVal = getattr(self, valName);
                setattr(self, valName, self.metadataUpdateInfo.updateFunc(recordVal, selfVal, valName, record)) 
        def getJsonableObject(self):
            return OrderedDict([(kwarg, getattr(self, kwarg)) for kwarg in metadataValNameToMetadataInfoLookup]);
        def defaultInit(cls):
            #set everything to None by default
            kwargs = dict([(kwarg, None) for kwarg in metadataValNameToMetadataInfoLookup]); 
            return cls(**kwargs);            
    return UpdateBestMetadataClass;

class SimpleJsonableRecordsHolder(object):
    def __init__(self, records):
        self.records = records;
    def addRecord(self, record):
        self.records.append(record);
    def getJsonableObject(self):
        return [record.getJsonableObject() for record in self.records];
    @classmethod
    def defaultInit(cls):
        return cls(records=[]);
    def getRecords(self):
        return self.records;

def getSortedJsonableRecordsHolderClass(keyFunc):
    class SortedJsonableRecordsHolder(SimpleJsonableRecordsHolder):
        keyFunc=keyFunc
        def __init__(self, records):
            """
                keyFunc: the function provided to sorted to sort
                    the records
            """
            super(SortedJsonableRecordsHolder, self).__init__(records);
        def addRecord(self, record):
            self.records.append(record);
            self.records = sorted(self.records, key = self.keyFunc);

class JsonDb(object):
    metadata_key = "metadata";
    records_key = "records";
    allKeys=[metadata_key, records_key];
    def __init__(self, jsonableRecordsHolder, metadata=None, callbacks_afterAdd=[]):
        self.metadata = metadata;
        self.records = jsonableRecordsHolder;
        self.callbacks_afterAdd=callbacks_afterAdd;
    def getJsonableObject(self):
        return OrderedDict([(self.metadata_key, self.metadata.getJsonableObject() if self.metadata is not None else None)
                            ,(self.records_key, self.jsonableRecords.getJsonableObject())]); 
    def addRecord(self, record):
        self.records.addRecord(record);
        if (self.metadata is not None):
            self.metadata.updateForRecord(record);
        for callback in self.callbacks_afterAdd:
            callback(record, self);
    @classmethod
    def getFactory(cls, JsonableRecordClass, JsonableRecordsHolderClass, MetadataClass=None):
        return cls.Factory(cls, JsonableRecordClass, JsonableRecordsHolderClass, MetadataClass=MetadataClass); 
    class Factory(object):
        def __init__(self, JsonDbClass, JsonableRecordClass, JsonableRecordsHolderClass, MetadataClass, callbacks_afterAdd):
            self.JsonDbClass = JsonDbClass;
            self.MetadataClass = MetadataClass;
            self.JsonableRecordClass = JsonableRecordsClass;
            self.JsonableRecordsHolderClass = JsonableRecordsHolderClass;
            self.callbacks_afterAdd = callbacks_afterAdd;
        def constructFromJson(self, parsedJson):
            return self.JsonDbClass(metadata=None if self.MetadataClass is None else self.MetadataClass.constructFromJson(parsedJson[self.JsonDbClass.metadata_key])
                                    , jsonableRecords=self.JsonableRecordsHolderClass(
                                        [self.JsonableRecordClass.constructFromJson(record)
                                            for record in parsedJson[self.JsonDbClass.records_key]])
                                    , callbacks_afterAdd=self.callbacks_afterAdd);
        def constructFromJsonFile(self, jsonFileHandle):
            parsedJson = util.parseYamlFile(jsonFileHandle);
            return self.constructFromJson(parsedJson); 
        def defaultInit(self):
            return self.JsonDbClass(metadata=self.MedataClass.defaultInit()
                        , jsonableRecords=self.JsonableRecordsHolderClass.defaultInit());

class AbstractJsonableRecord(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getJsonableObject(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def constructFromJson(cls, jsonRecord):
        """
            This should be implemented as a class
                method
        """   
        raise NotImplementedError();

def getKwargsJsonableRecord(kwargsOrder):
    class KwargsJsonableRecord(AbstractJsonableRecord):
        __metaclass__ = abc.ABCMeta
        kwargsOrder = kwargsOrder;
        def __init__(self, **kwargs):
            self._kwargs = kwargs;
            self.__dict__.update(kwargs); 
        def getJsonableObject(self):
            return OrderedDict([(keyword, self._kwargs[keyword]) for keyword in self.kwargsOrder]); 
        @classmethod
        def constructFromJson(cls, jsonRecord):
            return cls(**jsonRecord); 

def addRecordToFile(record, jsonDbFactory, jsonFile):
    import os;
    if (os.exists(jsonFile)):
        jsonDb = jsonDbFactory.constructFromJsonFile(fp.getFileHandle(jsonFile));
    else:
        jsonDb = jsonDbFactory.defaultInit();
    jsonDb.addRecord(record);
    writeRecordsToFile(jsonFile, jsonDb);  

def writeToFile(jsonFile, jsonDb):
    import os;
    if (os.exists(jsonFile)):
        fileHandle = BackupForWriteFileHandle(jsonFile);    
    else:
        fileHandle = fp.getFileHandle(jsonFile);
    try:
        fileHandle.write(util.formattedJsonDump([jsonDb.getJsonableObject()]));
        fileHandle.close();
    except e:
        fileHandle.restore();  

