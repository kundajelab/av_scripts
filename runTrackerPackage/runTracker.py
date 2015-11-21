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
sys.path.insert(0,scriptsDir+"/jsondbPackage");
import jsondb;
import pathSetter;
import util;
import fileProcessing as fp;
import abc;
from collections import namedtuple

runTrackerEmail = "bestestFramework@stanford.edu"
class RunAndAddRecords(object):
    def __init__(self, cmdKwargsGenerator, recordFromCmdKwargs, addRecordFunction):
        """
            cmdKwargsGenerator: instance of AbstractCmdKwargsGenerator
            recordFromCmdKwargs: instance of AbstractRecordFromCmdKwargs
            addRecordFunction: just a function that adds the records to the db
        """
        assert cmdKwargsGenerator is not None;
        assert recordFromCmdKwargs is not None;
        assert addRecordFunction is not None;
        self.cmdKwargsGenerator=cmdKwargsGenerator;
        self.recordFromCmdKwargs=recordFromCmdKwargs;
        self.addRecordFunction=addRecordFunction;
    def runAndAddRecords(self, numTrials):
        consecutiveFailedRecordAdds = 0;
        for i in xrange(numTrials):
            print("Running trial "+str(i));
            kwargs = self.cmdKwargsGenerator.generateCmdKwargs(); 
            record = self.recordFromCmdKwargs.getRecordFromCmdKwargs(**kwargs); 
            if (record is not None):
                consecutiveFailedRecordAdds=0;
                self.addRecordFunction(record);
            else:
                consecutiveFailedRecordAdds += 1;
                print("Skipping record add; consecutive failed adds:",consecutiveFailedRecordAdds)
                if (consecutiveFailedRecordAdds == 3):
                    raise RuntimeError(str(consecutiveFailedRecordAdds)+" consecutive failed record adds. Ending.");

#warning: probably does not play nice with threads
def getAddRecordAndSaveDbFunction(dbFactory, dbFile):
    def addRecordFunc(record):
        jsondb.addRecordToFile(record, dbFactory, dbFile);
    return addRecordFunc;
 
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
    def getRecordFromCmdKwargs(self, **cmdKwargs):
        try:
            lines = self.linesFromCmdKwargs.getLines(**cmdKwargs);
            recordMaker = self.makeRecordFromLines_producer();
            self.logger.log("Parsing stdout contents of function call...\n")
            for line in lines:
                self.logger.log(line);
                self.logger.log("\n");
                recordMaker.processLine(line);
                if (recordMaker.isRecordReady()):
                    return recordMaker.getRecord(**cmdKwargs);
            self.logger.log("...Done parsing stdout contents of function call\n")
            #if you get here, it means you couldn't make the record 
            self.logger.log("Error! Unable to make a record! Info: "
                            +recordMaker.getInfoOnStatus());
            raise RuntimeError("Unable to make record; info:\n"
                                +recordMaker.getInfoOnStatus()
                                +"\nlog file: "+self.logger.getInfo());
        except Exception as e:
            traceback=util.getErrorTraceback();
            emailError(self.options, self.logger.getInfo(), traceback);
            self.logger.log("Error!\n"+traceback+"\n");
            print("caught traceback: "+traceback);
         
def emailError(options, logFileInfo, traceback):
    if (options.emailMode not in [EmailModes.noEmails]):
        util.sendEmails(options.emails, runTrackerEmail
                        ,"Error when running "+options.jobName
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
    def getInfoOnStatus(self):
        """
            Return any info that may be useful
                for debugging why the record was
                not created
        """
        raise NotImplementedError();
    @abc.abstractmethod
    def getRecord(self, **commandKwargs):
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
    def getKwargNames(self):
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
        assert kwargsMakers is not None;
        assert recordMakerFunc is not None;
        self.kwargsMakers = kwargsMakers;
        self.recordMakerFunc = recordMakerFunc;
    def processLine(self, line):
        for kwargsMaker in self.kwargsMakers:
            if (not kwargsMaker.areKwargsReady()):
                kwargsMaker.processLine(line);
    def isRecordReady(self):
        return all([kwargsMaker.areKwargsReady() for kwargsMaker in self.kwargsMakers]); 
    def getInfoOnStatus(self):
        finishedKwargs = [x.getKwargNames() for x in 
                            self.kwargsMakers if x.areKwargsReady()];
        unfinishedKwargs = [x.getKwargNames() for x in 
                            self.kwargsMakers if (not x.areKwargsReady())];
        return ("Undetected kwargs: "+str(unfinishedKwargs)+"\n"
                "Detected kwargs: "+str(finishedKwargs))
    def getRecord(self, **commandKwargs):
        kwargs = {};
        for kwargsMaker in self.kwargsMakers:
            kwargs.update(kwargsMaker.getKwargs());
        kwargs.update(commandKwargs); 
        return self.recordMakerFunc(**kwargs);

def get_makeRecordFromLines_producer(recordMakerFunc, kwargsMakers_producer):
    """
        returns a function that produces a MakeRecordFrom_MakeKwargsFromLines instance.
        Uses kwargsMakers_producer to instantiate fresh kwargsMakers every time.
    """
    assert recordMakerFunc is not None;
    assert kwargsMakers_producer is not None;
    return lambda: MakeRecordFrom_MakeKwargsFromLines(
                        kwargsMakers=kwargsMakers_producer()
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
    def getKwargNames(self):
        return [self.kwargName];
    def getKwargs(self):
        assert self.val is not None;
        assert self.areKwargsReady();
        return {self.kwargName: self.val}; 

"""
class FixedKwargs(Abstract_MakeKwargsFromLines):
    #always returns the same kwargs
    def __init__(self, **kwargs):
        self.kwargs = kwargs;
    def processLine(self, line):
        pass;
    def areKwargsReady(self):
        return True;
    def getKwargs(self):
        return self.kwargs;
"""

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
        
class LinesFromFunctionStdout_NoProcessSpawned(AbstractMakeLinesFromCmdKwargs):
    def __init__(self, func, logger=None, emailErrorFunc=None):
        self.logger=logger;
        self.emailErrorFunc = emailErrorFunc;
        self.func = util.redirectStdoutToString(func, logger=logger, emailErrorFunc=emailErrorFunc); 
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

def getBestUpdateFunc(isLargerBetter, callbacksIfUpdated):
    """
        updateFunc to be provided to jsondb.MetadataUpdateInfo;
            updates a metadata field to keep track of the best.
    """
    def updateFunc(newVal, originalVal, valName=None, record=None):
        update=False;
        if originalVal is None:
            update = True;
        else:
            if isLargerBetter:
                if (newVal > originalVal):
                    update = True;
            else:
                if (newVal < originalVal):
                    update = True; 
        if (update):
            for callbackIfUpdated in callbacksIfUpdated:
                callbackIfUpdated(newVal, originalVal, valName, record);
            return newVal;
        else:
            return originalVal;
    return updateFunc;

def getPrintAddedRecordCallback():
    def callback(record, db):
        print("--Record added:--")  
        print(util.formattedJsonDump(record.getJsonableObject()));
        print("-----------------") 
    return callback;
def getEmailRecordAddedCallback(emailOptions):
    def callback(record, db):
        subject = "Record added for "+emailOptions.jobName
        contents = util.formattedJsonDump(record.getJsonableObject());
        util.sendEmails(emailOptions.toEmails, emailOptions.fromEmail, subject, contents);
    return callback; 
def getContents(valName, newVal, originalVal, record):
    contents = ("New best: "+valName+": "+str(newVal)+"\n" 
                +"Previous best "+valName+": "+str(originalVal)+"\n"
                +"Record:\n"+util.formattedJsonDump(record.getJsonableObject()))
    return contents; 
def getPrintIfNewBestCallback():
    def callback(newVal, originalVal, valName, record):
        contents = getContents(valName, newVal, originalVal, record);
        print("-------New best!-------")
        print(contents); 
        print("-----------------------");
    return callback;
EmailOptions = namedtuple("EmailOptions", ["toEmails", "fromEmail", "jobName", "emailMode"]);
def getEmailIfNewBestCallback(emailOptions):
    """
        a callback to send an email when a new 'best' is attained.
    """
    def emailCallback(newVal, originalVal, valName, record):
        subject = "New best "+valName+" for "+emailOptions.jobName
        contents = getContents(valName, newVal, originalVal, record);
        util.sendEmails(emailOptions.toEmails, emailOptions.fromEmail, subject, contents);
    return emailCallback;

PerfToTrackOptions = namedtuple("PerfToTrackOptions", ["perfAttrName", "isLargerBetter"]);
def getJsonDbFactory(emailOptions, perfToTrackOptions, JsonableRecordClass):
    """
        Returns a json db factory that keeps track of the best of some
            attribute and also maintains records in sorted order
            of that attribute.
    """
    keyFunc = lambda x: ((-1 if perfToTrackOptions.isLargerBetter else 1)*getattr(x,perfToTrackOptions.perfAttrName))
    JsonableRecordsHolderClass = jsondb.getSortedJsonableRecordsHolderClass(keyFunc=keyFunc); 
    callbacksIfUpdated = [getPrintIfNewBestCallback()];
    if emailOptions is not None and emailOptions.emailMode in [EmailModes.allEmails, EmailModes.errorsAndNewBest]:
        callbacksIfUpdated.append(getEmailIfNewBestCallback(emailOptions));
    callbacks_afterAdd = [getPrintAddedRecordCallback()];
    if (emailOptions is not None and emailOptions.emailMode in [EmailModes.allEmails]):
        callbacks_afterAdd.append(getEmailRecordAddedCallback(emailOptions)); 

    MetadataClass = jsondb.getUpdateValsMetadataClass(
                        [jsondb.MetadataUpdateInfo(
                            valName=perfToTrackOptions.perfAttrName
                            ,updateFunc=getBestUpdateFunc(
                                isLargerBetter=perfToTrackOptions.isLargerBetter
                                ,callbacksIfUpdated=callbacksIfUpdated)
                            )]); 
    jsonDbFactory = jsondb.JsonDb.getFactory(JsonableRecordClass=JsonableRecordClass
                            ,JsonableRecordsHolderClass=JsonableRecordsHolderClass
                            ,MetadataClass=MetadataClass
                            ,callbacks_afterAdd=callbacks_afterAdd); 
    return jsonDbFactory; 

EmailModes = util.enum(noEmails="noEmails", onlyErrorEmails="onlyErrorEmails", errorsAndNewBest="errorsAndNewBest", allEmails="allEmails"); 
def addRunTrackerArgumentsToParser(parser):
    parser.add_argument("--emails", nargs="+", required=True, help="Provide a dummy val if don't want emails");
    parser.add_argument("--emailMode", choices=EmailModes.vals, default=EmailModes.errorsAndNewBest);
    parser.add_argument("--jobName", required=True, help="Used to create email subjects and log files");
    parser.add_argument("--logFile");
    parser.add_argument("--jsonDbFile", required=True, help="Used to save the records");



