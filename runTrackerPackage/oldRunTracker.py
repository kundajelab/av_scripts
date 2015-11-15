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
from jsonDbPackage import jsondb;

def addRunTrackerArgumentsToParser(parser):
    parser.add_argument("--email", required=True, help="Provide a dummy val if don't want emails");
    parser.add_argument("--doNotEmail", action="store_true");
    parser.add_argument("--jobName", required=True, help="Used to create email subjects and log files");
    parser.add_argument("--logFile");

def runJob(commandArgs, recordMaker, db, logger, errorAction, emailers):
    import subprocess;
    popen = subprocess.Popen(commandArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines_iterator = iter(popen.stdout.readline, b"")  
    for line in lines_iterator:
        recordMaker.processLine(line);
        for emailer in emailers:
            emailer.processLine(line); 
        logger.write(line);
    exitCode = popen.returncode
    if (exitCode != 0):
        if errorAction is not None:
            errorAction(commandArgs, exitCode, logger); 
        raise subprocess.ProcessException(commandArgs, exitCode, "output at: "+logger.getInfo()) 
    else:
        record = recordMaker.getRecord(command=" ".join(commandArgs));
        db.addRecord(record);

def runJobsWithArgsGenerator(argsGenerator, recordMakerFactory, db, logger, errorAction, emailers, dbfile=None):
    for commandArgs in argsGenerator:
        runJob(commandArgs, recordMakerFactor.newRecordMaker(), db, logger, errorAction, emailers);
        if dbfile is not None:
            import jsondb;
            jsondb.writeToFile(dbFile, db);    
    logger.close();

def getEmailWhenErrorAction(email):
   raise NotImplementedError(); #TODO 

class AbstractLogger(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def write(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def getInfo(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def close(self):
        raise NotImplementedError();

class FileLogger(AbstractLogger):
    def __init__(self, logFileName):
        self.logFileName = logFileName;
        self.logFileHandle = fp.getFileHandle(logFileName, 'a');
    def write(self, toWrite):
        self.logFileHandle.write(toWrite);
    def getInfo(self):
        return self.logFileName;
    def close(self):
        self.logFileHandle.close();

class AbstractRecordMaker(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def processLine(self, line):
        raise NotImplementedError(); 
    @abc.abstractmethod
    def isRecordReady(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def getRecord(self, commandArgs):
        raise NotImplementedError();

class RecordMakerFromKwargsMakers(AbstractRecordMaker):
    def __init__(self, kwargsMakers, recordMakerFunc):
        self.kwargsMakers = kwargsMakers;
        self.recordMakerFunc = recordMakerFunc;
    def processLine(self, line):
        for kwargsMaker in kwargsMakers:
            if (not kwargsMaker.areKwargsReady()):
                kwargsMaker.processLine(line);
    def isRecordReady(self):
        return all([kwargsMaker.areKwargsReady() for kwargsMaker in self.kwargsMakers]); 
    def getRecord(self, commandArgs):
        kwargs = {};
        for kwargsMaker in self.kwargsMakers:
            kwargs.update(kwargsMaker.getKwargs());
        return self.recordMakerFunc(commandArgs=commandArgs, **kwargs);

class AbstractKwargsMaker(object):
    __metaclass__ = abc.ABCMeta 
    @abc.abstractmethod
    def processLine(self, line):
        raise NotImplementedError();
    @abc.abstractmethod
    def areKwargsReady(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def getKwargs(self):
        raise NotImplementedError();

class SimpleRegexKwargsMaker(AbstractKwargsMaker):
    def __init__(self, kwargName, kwargTypeCast, regex):
        import re;
        self.kwargName = kwargName
        self.kwargTypeCast = kwargTypeCast
        self.pattern = re.compile(regex)
        self.ready = False;
        self.val = None;
    def processLine(self, line):
        match = self.pattern.search(line);
        if match is not None:
            self.val = self.kwargTypeCast(match);
    def areKwargsReady(self):
        return self.ready;
    def getKwargs(self):
        assert self.val is not None;
        assert self.areKwargsReady();
        return {self.kwargName: self.val}; 

"""         
class AbstractCommandRecord(jsondb.AbstractJsonableRecord):
    command_key="command"
    allKeys = [commandArgs_key]
    def __init__(self, command):
        self.command = command;
    def getJsonableObject(self):
        return OrderedDict([(keyName, getattr(self,keyName)) for keyName in self.allKeys]);
    @classmethod
    def constructFromJson(cls, jsonRecord):
        return cls(cls.getKwargsForConstructor(jsonRecord));
    @classmethod
    def getKwargsForConstructor(cls, jsonRecord):
        toReturn = {};
        for key in cls.allKeys:
            toReturn[key] = jsonRecord[key];
        return toReturn;   
    def __str__(self):
        return "\n".join([keyName+": "+str(getattr(self, keyName))] for
                            keyName in self.allKeys]);
"""
