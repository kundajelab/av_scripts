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

runTrackerEmail = "bestestFramework@stanford.edu"
class RunAndAddRecords(object):
    def __init__(self, cmdKwargsGenerator, recordFromCmdKwargs, addRecordFunction):
        """
            cmdKwargsGenerator: instance of AbstractCmdKwargsGenerator
            recordFromCmdKwargs: instance of AbstractRecordFromCmdKwargs
            addRecordFunction: just a function that adds the records to the db
        """
        self.cmdKwargsGenerator=cmdKwargsGenerator;
        self.recordFromCmdKwargs=recordFromCmdKwargs;
        self.addRecordFunction=addRecordFunction;
    def runAndAddRecords(self, numTrials):
        for i in xrange(numTrials):
            kwargs = self.cmdKwargsGenerator.generateCmdKwargs(); 
            record = self.recordFromCmdKwargs.getRecordFromCmdKwargs(**kwargs); 
            self.addRecordFunction(record);

#warning: probably does not play nice with threads
def getAddRecordAndSaveDbFunction(dbFactory, dbFile):
    def addRecordFunc(record):
        jsondb.addRecordToFile(record, dbFactory, dbFile);
 
class AbstractCmdKwargsGenerator(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def generateCmdKwargs(self):
        raise NotImplementedError();

class CmdKwargsFromManager(AbstractCmdKwargsGenerator):
    def __init__(self, managerToCmdKwargs, manager):
        self.managerToCmdKwargs = managerToCmdKwargs;
        self.manager = manager;
    def generateCmdKwargs(self):
        self.manager.prepareNextSet(); 
        return self.managerToCmdKwargs(self.manager); 

class AbstractRecordFromCmdKwargs(object):
    """
        given kwargs for a command, eg, launching a job,
            returns a record to go in a db
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getRecordFromCmdKwargs(self, **cmdKwargs):
        raise NotImplementedError();
    
class RecordFromCmdKwargsUsingLines(AbstractRecordFromCmdKwargs):
    def __init__(self, options, linesFromCmdKwargs, makeRecordFromLines_producer, logger):
        """
            linesFromCmdKwargs: instance of AbstractMakeLinesFromCmdKwargs
            makeRecordFromLines_producer: returns an instance of AbstractMakeRecordFromLines
            logger: instance of AbstractLogger    
        """
        self.options = options;
        self.linesFromCmdKwargs=linesFromCmdKwargs;
        self.makeRecordFromLines_producer = makeRecordFromLines_producer;
        self.logger = logger;
    def getRecordFromCmdKwargs(self, **cmdKwags):
        try:
            lines = self.linesFromCmdKwargs.getLines(**cmdKwargs);
            recordMaker = self.recordMakerFromLines_factory.get_recordFromLines();
            for line in lines:
                self.logger.log(line);
                recordMaker.processLine(line);
                if (recordMaker.isRecordReady()):
                    return recordMaker.getRecord();
            #if you get here, it means you couldn't make the record 
            logger.log("Error! Unable to make a record!");
            raise RuntimeError("Unable to make record; log file: "+self.logger.getInfo());
        except Exception as e:
            emailError(self.logger.getInfo());
            raise e; 
         
def emailError(logFileInfo):
    if (not options.doNotEmail):
        traceback = util.getErrorTraceback();
        util.sendEmail(self.options.email, runTrackerEmail
                        ,"Error when running "+self.options.jobName
                        ,"Log file: "+logFileInfo+"\n"+traceback);

class AbstractMakeLinesFromCmdKwargs(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getLines(self, **cmdKwargs):
        """
            given some kwargs for a command, eg,  launching a job,
            returns a lines iterator
        """
        raise NotImplementedError();

class MakeLines

class AbstractMakeRecordFromLines(object):
    """
        pass it a series of output lines
        to make a record
    """
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

class Abstract_MakeKwargsFromLines(object):
    """
        pass it a series of output lines to
            make kwargs; used by record makers
    """
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

class MakeRecordFrom_MakeKwargsFromLines(AbstractMakeRecordFromLines):
    def __init__(self, kwargsMakers, recordMakerFunc):
        """
            in order to use: must define a recordMakerFunc
                that uses the commandKwargs, and also a
                series of kwargsMakers for all the kwargs
                that are parsed from the stream.
        """
        self.kwargsMakers = kwargsMakers;
        self.recordMakerFunc = recordMakerFunc;
    def processLine(self, line):
        for kwargsMaker in kwargsMakers:
            if (not kwargsMaker.areKwargsReady()):
                kwargsMaker.processLine(line);
    def isRecordReady(self):
        return all([kwargsMaker.areKwargsReady() for kwargsMaker in self.kwargsMakers]); 
    def getRecord(self, **commandKwargs):
        kwargs = {};
        for kwargsMaker in self.kwargsMakers:
            kwargs.update(kwargsMaker.getKwargs());
        return self.recordMakerFunc(**commandKwargs, **kwargs);

def get_makeRecordFromLines_producer(recordMakerFunc, kwargsMakers_producer):
    """
        returns a function that produces a MakeRecordFrom_MakeKwargsFromLines instance.
        Uses kwargsMakers_producer to instantiate fresh kwargsMakers every time.
    """
    return lambda: runTracker.MakeRecordFrom_MakeKwargsFromLines(
                        kwargsMakers=kwargsMakers_producer
                        ,recordMakerFunc=recordMakerFunc);  

class SimpleRegex_MakeKwargsFromLines(Abstract_MakeKwargsFromLines):
    def __init__(self, kwargName, kwargTypeCast, regex, groupIndex=1, startLookingRegex=None):
        """
            startLookingRegex: only try to match regex AFTER you have seen startLookingRegex
        """
        import re;
        self.kwargName = kwargName
        self.kwargTypeCast = kwargTypeCast
        self.pattern = re.compile(regex)
        self.groupIndex = groupIndex;
        self.ready = False;
        self.val = None;
        self.startLookingPattern = None if startLookingRegex is None else re.compile(startLookingRegex);
        self.startLooking = startLookingRegex is None;
    def processLine(self, line):
        if (self.startLooking): 
            match = self.pattern.search(line);
            if match is not None:
                self.val = self.kwargTypeCast(match.group(self.groupIndex)); 
                self.ready = True;
        else:
            assert self.startLookingPattern is not None;
            match = self.startLookingPattern.search(line);
            if (match is not None):
                self.startLooking = True;
    def areKwargsReady(self):
        return self.ready;
    def getKwargs(self):
        assert self.val is not None;
        assert self.areKwargsReady();
        return {self.kwargName: self.val}; 

class AbstractLogger(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def log(self):
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
    def log(self, toWrite):
        self.logFileHandle.write(toWrite);
    def getInfo(self):
        return self.logFileName;
    def close(self):
        self.logFileHandle.close();


class KickoffAndTrackRecords(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, recordMakerFactor, linesFactory):
        self.recordMakerFactory = recordMakerFactory;
        self.linesFactory = linesFactory;
    @abc.abstractmethod
    def getRecord(self, **kwargs):
        #return a db record. May do things
        #like logging.
        
class LinesFromFunctionStdout_NoProcessSpawned(AbstractMakeLinesFromCmdKwargs):
    def __init__(self, func):
        self.func = util.redirectStdoutToString(func); 
    def getLines(self, **cmdKwargs):
        lines = self.func(**cmdKwargs)
        return lines.split("\n")

#TODO: test
class LinesFromSpawnedProcess(AbstractMakeLinesFromCmdKwargs):
    def getLines(self, **cmdKwargs):
        """
            cmdKwargs should have 'args', and I can't think
                of anything else it should have.
        """
        assert 'args' in cmdKwargs;
        assert len(cmdKwargs.keys())==1;
        import subprocess;
        popen = subprocess.Popen(args=cmdKwargs['args'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = iter(popen.stdout.readline, b"") 
        return lines;

#CL = command line
def formatArgForCL(argName, argVal):
    return "--"+argName+" "+str(argVal);

def getBestUpdateFunc(isLargerBetter, callbackIfUpdated):
    """
        updateFunc to be provided to jsondb.MetadataUpdateInfo;
            updates a metadata field to keep track of the best.
    """
    def updateFunc(newVal, originalVal, valName=None, record=None):
        if originalVal is None:
            update = True;
        else:
            if largerIsBetter:
                if (newVal > originalVal):
                    update = True;
            else:
                if (newVal < originalVal):
                    update = True; 
        if (update):
            callbackIfUpdated(newVal, originalVal, valName, record);
            return newVal;
        else:
            return originalVal;

EmailOptions = namedtuple("EmailOptions", ["toEmail", "fromEmail", "jobName"]);
def getEmailIfNewBestCallback(emailOptions):
    """
        a callback to send an email when a new 'best' is attained.
    """
    def emailCallback(newVal, originalVal, valName, record):
        subject = "New best "+valName+" for "+emailOptions.jobName
        contents = ("New best: "+valName+": "+str(newVal)+"\n" 
                    +"Previous best "+valName+": "+str(originalVal)+"\n"
                    +"Record:\n"+util.formattedJsonDump(record.getJsonableObject()))
        util.sendEmail(emailOptions.toEmail, emailOptions.fromEmail, subject, contents);

PerfToTrackOptions = namedtuple("PerfToTrackOptions", ["perfAttrName", "isLargerBetter"]);
def getJsonDbFactory(emailOptions, perfToTrackOptions, JsonableRecordClass):
    """
        Returns a json db factory that keeps track of the best of some
            attribute and also maintains records in sorted order
            of that attribute.
    """
    keyFunc = lambda x: ((-1 if isLargerBetter else 1)*getattr(x,perfToTrackOptions.perfAttrName))
    JsonableRecordsHolderClass = jsondb.getSortedJsonableRecordsHolderClass(keyFunc=keyFunc); 
    MetadataClass = jsondb.getUpdateValsMetadataClass(
                        jsondb.MetadataUpdateInfo(
                            valName=perfToTrackOptions.perfAttrName
                            ,updateFunc=getBestUpdateFunc(
                                isLargerBetter=perfToTrackOptions.isLargerBetter
                                ,callbackIfUpdated=getEmailIfNewBestCallback(emailOptions))
                    )); 
    jsonDbFactory = jsondb.JsonDb.getJsonDbFactory(JsonableRecordClass=JsonableRecordClass
                            ,JsonableRecordsHolderClass=JsonableRecordsHolderClass
                            ,MetadataClass=MetadataClass); 
    return jsonDbFactory; 
    
def addRunTrackerArgumentsToParser(parser):
    parser.add_argument("--email", required=True, help="Provide a dummy val if don't want emails");
    parser.add_argument("--doNotEmail", action="store_true");
    parser.add_argument("--jobName", required=True, help="Used to create email subjects and log files");
    parser.add_argument("--logFile");
    parser.add_argument("--jsonDbFile", required=True, help="Used to save the records");



