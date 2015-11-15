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

def runAndAddRecords(numTrials, cmdKwargsGenerator, recordFromCmdKwargs, addRecordFunction):
    """
        cmdKwargsGenerator: instance of AbstractCmdKwargsGenerator
        recordMakerUsingKwargs: instance of AbstractRecordFromCmdKwargs
    """
    for i in xrange(numTrials):
        kwargs = cmdKwargsGenerator.generateCmdKwargs(); 
        record = recordFromCmdKwargs(**kwargs); 
        addRecordFunction(record);

#warning: probably does not play nice with threads
def getAddRecordAndSaveDbFunction(dbFactory, dbFile):
    from jsonDbPackage import jsondb;
    def addRecordFunc(record):
        jsondb.addRecordToFile(record, dbFactory, dbFile);
 
class AbstractCmdKwargsGenerator(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def generateCmdKwargs(self):
        raise NotImplementedError();

class CmdKwargsGeneratorFromManager(AbstractCmdKwargsGenerator):
    def __init__(self, managerToKwargs, manager):
        self.managerToKwargs = managerToKwargs;
        self.manager = manager;
    def generateCmdKwargs(self):
        self.manager.prepareNextSet(); 
        return self.managerToKwargs(self.manager); 

class AbstractRecordFromCmdKwargs(object):
    """
        given kwargs for a command, eg, launching a job,
            returns a record to go in a db
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def recordFromCmdKwargs(self, **cmdKwargs):
        raise NotImplementedError();
    
class RecordFromCmdKwargsUsingLinesIterator(AbstractLinesIteratorFromCmdKwargs):
    def __init__(self, options, linesIteratorFromCmdKwargs, recordMakerFromLinesIterator_factory, logger):
        """
            linesIteratorFromCmdKwargs: instance of AbstractLinesIteratorFromCmdKwargs
            recordMakerFromLinesIterator_factory: instance of AbstractRecordMakerFromLinesIterator_Factory
            logger: instance of AbstractLogger    
        """
        self.options = options;
        self.linesIteratorFromCmdKwargs=linesIteratorFromCmdKwargs;
        self.recordMakerFromLinesIterator_factory=recordMakerFromLinesIterator_factory;
        self.logger = logger;
    def recordFromCmdKwargs(self, **cmdKwags):
        try:
            linesIterator = self.linesIteratorFromCmdKwargs.getLinesIterator(**cmdKwargs);
            recordMaker = self.recordMakerFromLinesIterator_factory.getRecordMakerFromLinesIterator();
            for line in linesIterator:
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
        util.sednEmail(self.options.email, "bestestFramework@stanford.edu"
                        ,"Error when running "+self.options.jobName
                        ,"Log file: "+logFileInfo+"\n"+traceback);

class AbstractLinesIteratorFromCmdKwargs(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getLinesIterator(self, **cmdKwargs):
        """
            given some kwargs for a command, eg,  launching a job,
            returns a lines iterator
        """
        raise NotImplementedError();

class AbstractRecordMakerFromLinesIterator_Factory(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getRecordMakerFromLinesIterator(self):
        raise NotImplementedError(); 

class AbstractRecordMakerFromLines(object):
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

class AbstractKwargsMaker(object):
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

class RecordMakerFromKwargsMakers(AbstractRecordMaker):
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

class SimpleRegexKwargsMaker(AbstractKwargsMaker):
    def __init__(self, kwargName, kwargTypeCast, regex, groupIndex, startLookingRegex=None):
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
    def __init__(self, recordMakerFactor, linesIteratorFactory):
        self.recordMakerFactory = recordMakerFactory;
        self.linesIteratorFactory = linesIteratorFactory;
    @abc.abstractmethod
    def getRecord(self, **kwargs):
        #return a db record. May do things
        #like logging.
        
class LinesIteratorFromFunctionStdout_NoProcessSpawned(AbstractLinesIteratorFactory):
    def __init__(self, func):
        self.func = util.redirectStdoutToString(func); 
    def getLinesIterator(self, *args, **kwargs):
        lines = self.func(*args, **kwargs)
        return lines.split("\n")

#TODO: test
class LinesIteratorFromSpawnedProcess(AbstractLinesIteratorFactory):
    def getLinesIterator(self, commandArgs):
        import subprocess;
        popen = subprocess.Popen(commandArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        linesIterator = iter(popen.stdout.readline, b"") 
        return linesIterator;



def addRunTrackerArgumentsToParser(parser):
    parser.add_argument("--email", required=True, help="Provide a dummy val if don't want emails");
    parser.add_argument("--doNotEmail", action="store_true");
    parser.add_argument("--jobName", required=True, help="Used to create email subjects and log files");
    parser.add_argument("--logFile");
    parser.add_argument("--jsonDbFile", required=True, help="Used to save the records");



