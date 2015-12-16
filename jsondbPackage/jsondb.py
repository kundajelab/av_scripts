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
from collections import OrderedDict

"""
Planned tests for jsondb file:
- getUpdateValsMetadataClass
- getSortedJsonableRecordsHolderClass
- getKwargsJsonableRecord
- addRecordToFile
"""

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

MetadataUpdateInfo = namedtuple("MetadataUpdateInfo", ["metadataAttrName", "recordAttrName", "updateFunc", "initVal"]);
NumRecordsMetadataUpdateInfo = MetadataUpdateInfo(
                                metadataAttrName="numRecords"
                                ,recordAttrName=None
                                ,updateFunc=lambda recordVal, selfVal, attrName, record: selfVal+1
                                ,initVal=0);
def getUpdateValsMetadataClass(metadataUpdateInfos, otherFields):
    """
        A metadata class that updates some values based on
            the records added. metadataUpdateInfos contains
            the info for how to do any updates based on newly
            added records. OtherFields are any other fields
            that may exist in the db.
    """
    metadataValNameToMetadataInfoLookup = OrderedDict([(x.metadataAttrName, x) for x in metadataUpdateInfos]);
    fieldOrdering = [x for x in metadataValNameToMetadataInfoLookup.keys()]+otherFields;
    class UpdateValsMetadataClass(AbstractMetadataClass):
        def __init__(self, **kwargs):
            for field in fieldOrdering:
                if (field not in kwargs):
                    kwargs[field] = None; 
            for kwarg in kwargs:
                if kwarg not in fieldOrdering: #N.B.: inefficient array lookup!
                    raise RuntimeError(kwarg+" not in declared fields; valid fields are: "
                                        +str(fieldOrdering)); 
            self._kwargs = kwargs;
        def updateForRecord(self, record):
            """
                refers to metadataUpdateInfos to perform the update
            """
            for metadataUpdateInfo in metadataUpdateInfos:
                recordVal = (getattr(record, metadataUpdateInfo.recordAttrName)
                                if metadataUpdateInfo.recordAttrName is not None else None);
                selfVal = self.getField(metadataUpdateInfo.metadataAttrName);
                self.setField(metadataUpdateInfo.metadataAttrName
                                , metadataUpdateInfo.updateFunc(recordVal, selfVal
                                    , metadataUpdateInfo.metadataAttrName, record)) 
        def getField(self, fieldName):
            return self._kwargs[fieldName];
        def setField(self, fieldName, fieldVal):
            self._kwargs[fieldName] = fieldVal;
        def getJsonableObject(self):
            return OrderedDict([(kwarg, self.getField(kwarg)) for kwarg in fieldOrdering]);
        @classmethod
        def defaultInit(cls):
            kwargs = {};
            for kwarg in fieldOrdering:
                if kwarg in metadataValNameToMetadataInfoLookup:
                    kwargs[kwarg] = metadataValNameToMetadataInfoLookup[kwarg].initVal;
                else:
                    kwargs[kwarg] = None;
            return cls(**kwargs);            
    return UpdateValsMetadataClass;

class SimpleJsonableRecordsHolder(object):
    def __init__(self, records):
        self.records = records;
    def getNumRecords(self):
        return len(self.records);
    def addRecord(self, record):
        record.setRecordNo(self.getNumRecords());
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
        def __init__(self, records):
            """
                keyFunc: the function provided to sorted to sort
                    the records
            """
            super(SortedJsonableRecordsHolder, self).__init__(records);
            self.keyFunc=keyFunc;
        def addRecord(self, record):
            super(SortedJsonableRecordsHolder, self).addRecord(record)
            self.records = sorted(self.records, key = self.keyFunc);
        def getIthSortedRecord(self, i):
            """
                zero-based
            """
            return self.records[i];
    return SortedJsonableRecordsHolder;

class JsonDb(object):
    metadata_key = "metadata";
    records_key = "jsonableRecordsHolder";
    allKeys=[metadata_key, records_key];
    def __init__(self, jsonableRecordsHolder, metadata, callbacks_beforeAdd, callbacks_afterAdd):
        self.metadata = metadata;
        self.jsonableRecordsHolder = jsonableRecordsHolder;
        self.callbacks_beforeAdd = callbacks_beforeAdd;
        self.callbacks_afterAdd=callbacks_afterAdd;
    def getNumRecords(self):
        return self.jsonableRecordsHolder.getNumRecords();
    def getJsonableObject(self):
        return OrderedDict([(self.metadata_key, self.metadata.getJsonableObject() if self.metadata is not None else None)
                            ,(self.records_key, self.jsonableRecordsHolder.getJsonableObject())]); 
    def addRecord(self, record):
        for callback in self.callbacks_beforeAdd:
            callback(record, self);
        self.jsonableRecordsHolder.addRecord(record);
        if (self.metadata is not None):
            self.metadata.updateForRecord(record);
        for callback in self.callbacks_afterAdd:
            callback(record, self);
    @classmethod
    def getFactory(cls, JsonableRecordClass, JsonableRecordsHolderClass
                    , MetadataClass=None, callbacks_beforeAdd=[], callbacks_afterAdd=[]):
        assert JsonableRecordClass is not None;
        assert JsonableRecordsHolderClass is not None;
        assert MetadataClass is not None; #for now
        return cls.Factory(cls, JsonableRecordClass
                , JsonableRecordsHolderClass, MetadataClass=MetadataClass
                , callbacks_beforeAdd=callbacks_beforeAdd
                , callbacks_afterAdd=callbacks_afterAdd); 
    class Factory(object):
        def __init__(self, JsonDbClass, JsonableRecordClass
                , JsonableRecordsHolderClass, MetadataClass
                , callbacks_beforeAdd, callbacks_afterAdd):
            self.JsonDbClass = JsonDbClass;
            self.MetadataClass = MetadataClass;
            self.JsonableRecordClass = JsonableRecordClass;
            self.JsonableRecordsHolderClass = JsonableRecordsHolderClass;
            self.callbacks_beforeAdd = callbacks_beforeAdd;
            self.callbacks_afterAdd = callbacks_afterAdd;
        def constructFromJson(self, parsedJson):
            assert parsedJson is not None;
            return self.JsonDbClass(metadata=None if self.MetadataClass is None else self.MetadataClass.constructFromJson(parsedJson[self.JsonDbClass.metadata_key])
                                    , jsonableRecordsHolder=self.JsonableRecordsHolderClass(
                                        [self.JsonableRecordClass.constructFromJson(record)
                                            for record in parsedJson[self.JsonDbClass.records_key]])
                                    , callbacks_beforeAdd=self.callbacks_beforeAdd
                                    , callbacks_afterAdd=self.callbacks_afterAdd);
        def constructFromJsonFile(self, jsonFile):
            parsedJson = util.parseYamlFile(jsonFile);
            if parsedJson is None:
                raise RuntimeError("No json extracted from "+str(jsonFile));
            return self.constructFromJson(parsedJson); 
        def defaultInit(self):
            return self.JsonDbClass(metadata=self.MetadataClass.defaultInit()
                        , jsonableRecordsHolder=self.JsonableRecordsHolderClass.defaultInit()
                        , callbacks_beforeAdd=self.callbacks_beforeAdd
                        , callbacks_afterAdd=self.callbacks_afterAdd);

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
    @abc.abstractmethod
    def setRecordNo(self, recordNo):
        """
            Used for creating a record id for the db
        """
        raise NotImplementedError();
    @abc.abstractmethod
    def getRecordNo(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def getField(self, field):
        raise NotImplementedError();
    @abc.abstractmethod
    def setField(self, field):
        raise NotImplementedError();

def getKwargsJsonableRecord(kwargsOrder):
    recordNoKey="recordNo";
    if recordNoKey in kwargsOrder:
        raise RuntimeError(recordNoKey+" is a reserved keyword; can't have as field");
    class KwargsJsonableRecord(AbstractJsonableRecord):
        def __init__(self, **kwargs):
            self.kwargsOrder = [recordNoKey]+kwargsOrder;
            self._kwargs = kwargs;
            self.__dict__.update(kwargs); 
        def getJsonableObject(self):
            toReturn = OrderedDict();
            for keyword in self.kwargsOrder:
                if (keyword in self._kwargs):
                    toReturn[keyword] = self._kwargs[keyword];
                else:
                    toReturn[keyword] = None; 
            return toReturn;
        def setRecordNo(self, recordNo):
            assert recordNo is not None;
            assert recordNoKey not in self._kwargs;
            self._kwargs[recordNoKey] = recordNo;
        def getRecordNo(self):
            return self.getField(recordNoKey); 
        def getField(self, fieldName, noneIfAbsent=False):
            if (noneIfAbsent and fieldName not in self._kwargs):
                return None;
            return self._kwargs[fieldName];
        def setField(self, fieldName, fieldVal, allowOverwrite=False):
            if ((not allowOverwrite) and fieldName in self._kwargs):
                if self._kwargs[fieldName] != fieldVal:
                    raise RuntimeError(
                            "Trying to overwrite field "+str(fieldName)
                            +" with "+str(fieldVal)+" when current val"
                            +" is "+str(self.getField(fieldName))+"."
                            +" Enable allowOverwrite to get rid of this error"); 
            self._kwargs[fieldName] = fieldVal;
        def removeField(self, fieldName, errorIfAbsent=True):
            if ((not errorIfAbsent) and fieldName not in self._kwargs):
                return;
            del self._kwargs[fieldName];
        @classmethod
        def constructFromJson(cls, jsonRecord):
            assert jsonRecord is not None;
            return cls(**jsonRecord); 
    return KwargsJsonableRecord

def getDb(jsonDbFactory, jsonFile):
    if (os.path.exists(jsonFile)):
        jsonDb = jsonDbFactory.constructFromJsonFile(jsonFile);
    else:
        jsonDb = jsonDbFactory.defaultInit();
    return jsonDb; 

def addRecordToFile(record, jsonDbFactory, jsonFile):
    import time;
    lock = util.LockDir(jsonFile);
    time1 = time.time(); 
    try:
        jsonDb = getDb(jsonDbFactory, jsonFile);
        jsonDb.addRecord(record);
        writeToFile(jsonFile, jsonDb, lock=lock);  
    except Exception as e:
        lock.release(); 
        print("caught: "+util.getErrorTraceback());
        raise e;
    time2 = time.time();
    print('Reading/writing from db took %0.3f ms' % ((time2-time1)*1000.0))
    lock.release();

def addRecordToDbAndWriteToFile(record, jsonDb, jsonFile):
    import time;
    time1 = time.time(); 
    jsonDb.addRecord(record);
    writeToFile(jsonFile, jsonDb); 
    time2 = time.time();
    print('writing to db took %0.3f ms' % ((time2-time1)*1000.0))

def writeToFile(jsonFile, jsonDb, lock=None):
    import os;
    if (os.path.exists(jsonFile)):
        fileHandle = fp.BackupForWriteFileHandle(jsonFile);    
    else:
        fileHandle = fp.getFileHandle(jsonFile,'w');
    try:
        fileHandle.write(util.formattedJsonDump(jsonDb.getJsonableObject()));
        fileHandle.close();
    except Exception as e:
        if (hasattr(fileHandle, "restore")):
            fileHandle.restore();  
            if lock is not None:
                lock.release(); 
        else:
            print("Error occurred, no restore available");
        print("caught: "+util.getErrorTraceback());
        raise e;

