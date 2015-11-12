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

class AbstractJsonableRecord(object):
    __metaclass__ = abc.ABCMeta
    @abstractmethod
    def getJsonableObject(self):
        raise NotImplementedError();
    @abstractmethod
    def constructFromJson(cls, jsonRecord):
        """
            This should be implemented as a class
                method
        """   
        raise NotImplementedError();

def makeRecordsFromFile(jsonFile, JsonableRecordClass):
    """
        for now, the json db file is just an array of records
        Will use a yaml parser so i can handle comments and such
    """
    parsedJson = util.parseYamlFile(jsonFile); 
    jsonableRecords = [JsonableRecordClass.constructFromJson(jsonRecord)
                            for jsonRecord in parsedJson];
    return jsonableRecords;

def writeRecordsToFile(jsonFile, jsonableRecords):
    fileHandle = BackupForWriteFileHandle(jsonFile);    
    try:
        fileHandle.write(util.formattedJsonDump([jsonableRecords.getJsonableObject()]));
        fileHandle.close();
    except e:
        fileHandle.restore();  

