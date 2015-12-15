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
import shutil

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
    def runAndAddRecords(self, numTrials=None):
        consecutiveFailedRecordAdds = 0;
        i = 0;
        while (numTrials is None or i < numTrials):
            print("Running trial "+str(i));
            kwargs = self.cmdKwargsGenerator(); 
            record = self.recordFromCmdKwargs.getRecordFromCmdKwargs(**kwargs); 
            if (record is not None):
                consecutiveFailedRecordAdds=0;
                self.addRecordFunction(record);
            else:
                consecutiveFailedRecordAdds += 1;
                print("Skipping record add; consecutive failed adds:",consecutiveFailedRecordAdds)
                if (consecutiveFailedRecordAdds == 3):
                    raise RuntimeError(str(consecutiveFailedRecordAdds)+" consecutive failed record adds. Ending.");
            i += 1;

def getAddRecordAndSaveDbFunction(db, dbFile):
    def addRecordFunc(record):
        jsondb.addRecordToDbAndWriteToFile(record, db, dbFile);
    return addRecordFunc;
 
def getAddRecordToDbFileFunction(dbFactory, dbFile):
    def addRecordFunc(record):
        jsondb.addRecordToFile(record, dbFactory, dbFile);
    return addRecordFunc;
 
class AbstractCmdKwargsGenerator(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError();

class CmdKwargsFromManager(AbstractCmdKwargsGenerator):
    def __init__(self, managerToCmdKwargs, manager):
        self.managerToCmdKwargs = managerToCmdKwargs;
        self.manager = manager;
    def __call__(self):
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
    def getInfoOnStatus(self):
        raise NotImplementedError();
    @abc.abstractmethod
    def getKwargs(self):
        raise NotImplementedError();

class SubKwargsMakersHandler(object):
    def __init__(self, kwargsMakers):
        self.kwargsMakers = kwargsMakers;
    def processLine(self, line):
        for kwargsMaker in self.kwargsMakers:
            if (not kwargsMaker.areKwargsReady()):
                kwargsMaker.processLine(line);
    def isReady(self):
        return all([kwargsMaker.areKwargsReady() for kwargsMaker in self.kwargsMakers]); 
    def getInfoOnStatus(self):
        return "\n".join([x.getInfoOnStatus() for x in self.kwargsMakers]);
    def getKwargs(self):
        kwargs = {};
        for kwargsMaker in self.kwargsMakers:
            kwargs.update(kwargsMaker.getKwargs());
        return kwargs;

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
        self.subKwargsMakersHandler = SubKwargsMakersHandler(kwargsMakers);
        self.recordMakerFunc = recordMakerFunc;
    def processLine(self, line):
        self.subKwargsMakersHandler.processLine(line);
    def isRecordReady(self):
        return self.subKwargsMakersHandler.isReady();
    def getInfoOnStatus(self):
        return self.subKwargsMakersHandler.getInfoOnStatus();
    def getRecord(self, **commandKwargs):
        kwargs = self.subKwargsMakersHandler.getKwargs();
        return self.recordMakerFunc(kwargs, commandKwargs);

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
    def getInfoOnStatus(self):
        return self.kwargName+" is"+(" not" if (not self.ready) else "")+" ready";
    def getKwargs(self):
        assert self.val is not None;
        assert self.areKwargsReady();
        return {self.kwargName: self.val}; 

class SubKwargsWrapper(Abstract_MakeKwargsFromLines):
    def __init__(self, kwargName, subKwargsMakers):
        self.kwargName = kwargName;
        self.subKwargsMakersHandler = SubKwargsMakersHandler(subKwargsMakers);
    def processLine(self, line):
        self.subKwargsMakersHandler.processLine(line);
    def areKwargsReady(self):
        return self.subKwargsMakersHandler.isReady()
    def getInfoOnStatus(self):
        return ("For "+self.kwargName+"...\n"
                +self.subKwargsMakersHandler.getInfoOnStatus()
                +"\n...end"+self.kwargName);
    def getKwargs(self, **commandKwargs):
        subKwargs = self.subKwargsMakersHandler.getKwargs();
        return {self.kwargName: subKwargs};

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

def getBestUpdateFunc(isLargerBetter, metadataCallbacks):
    """
        updateFunc to be provided to jsondb.MetadataUpdateInfo;
            updates a metadata field to keep track of the best.
    """
    def updateFunc(newVal, originalVal, metadataAttrName, record=None):
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
        for metadataCallback in metadataCallbacks:
            metadataCallback(update, newVal
                , originalVal, metadataAttrName, record);
        if (update):
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
    def callback(update, newVal, originalVal, valName, record):
        if (update):
            contents = getContents(valName, newVal, originalVal, record);
            print("-------New best!-------")
            print(contents); 
            print("-----------------------");
    return callback;
        
EmailOptions = namedtuple("EmailOptions", ["toEmails", "fromEmail", "jobName", "emailMode"]);
def getEmailIfNewBestCallback(emailOptions, perfToTrackOptions):
    """
        a callback to send an email when a new 'best' is attained.
    """
    def emailCallback(update, newVal, originalVal, valName, record):
        if (update):
            if (perfToTrackOptions.thresholdPerfToEmailAt is None or
                util.isBetterOrEqual(newVal,perfToTrackOptions.thresholdPerfToEmailAt
                                ,perfToTrackOptions.isLargerBetter)):
                subject = "New best "+valName+" for "+emailOptions.jobName
                contents = getContents(valName, newVal, originalVal, record);
                util.sendEmails(emailOptions.toEmails, emailOptions.fromEmail, subject, contents);
    return emailCallback;

def renameFilesWithRecordNumberCallback(savedFilesTracker):
    def callback(record, jsonDb):
        prospectiveRecordNumber=jsonDb.getNumRecords();
        #rename all the files
        for (idx, aFile) in enumerate(savedFilesTracker.currentFiles):
            newName = fp.getFileNameParts(aFile).getFilePathWithTransformation(
                            lambda x: "record_"+str(prospectiveRecordNumber)+"_"+x) 
            os.rename(aFile, newName); 
            savedFilesTracker.currentFiles[idx] = newName;
    return callback;

def getSaveBestFilesCallback(perfToTrackOptions, savedFilesTracker):
    def callback(record, jsonDb):
        perfField = perfToTrackOptions.perfAttrName;
        recordPerf = record.getField(perfField);
        bestPerfSoFar = jsonDb.metadata.getField(perfField);
        if (util.isBetter(recordPerf, bestPerfSoFar, perfToTrackOptions.isLargerBetter)):
            newBestFiles=[];
            for currentFile in savedFilesTracker.currentFiles:
                bestFileName = savedFilesTracker.bestFileNameGivenCurrentFile(currentFile);
                print("Saving new best:",currentFile,"as",bestFileName) 
                shutil.copy(currentFile, bestFileName); 
                newBestFiles.append(bestFileName);
            oldBestPerfSavedFiles = jsonDb.metadata.getField(RunTrackerMetadataFields.bestPerfSavedFiles); 
            if (oldBestPerfSavedFiles is not None):
                for oldBestFile in oldBestPerfSavedFiles:
                    print("Removing old best:",oldBestFile);
                    os.remove(oldBestFile);
            jsonDb.metadata.setField(RunTrackerMetadataFields.bestPerfSavedFiles, newBestFiles)
    return callback;

def getSaveSomeFilesCallback(perfToTrackOptions, savedFilesTracker):
    def callback(record, jsonDb):
        #I think the db should be locked during all this so no issue
        #with the record number changing, I hope
        prospectiveRecordNumber = jsonDb.getNumRecords();
        
        #by default, do not save any files
        saveFiles = False; 
        #if at least one of the save file constrains is active, these
        #files may qualify for saving. Check to say if either are
        #satisfied.
        if (perfToTrackOptions.minThresholdPerfToSaveFiles is not None or
            savedFilesTracker.topNtoSave is not None):
            perf = record.getField(perfToTrackOptions.perfAttrName)
            #if the "minPerfThreshold" constraint is met (or it's not active)...
            if (perfToTrackOptions.minThresholdPerfToSaveFiles is None or
                    util.isBetterOrEqual(perf, perfToTrackOptions.minThresholdPerfToSaveFiles, perfToTrackOptions.isLargerBetter)):
                if (perfToTrackOptions.minThresholdPerfToSaveFiles is not None):
                    print("Min threshold constraint satisfied for "+str(prospectiveRecordNumber)+"; "
                        +str(perf)+" vs "+str(perfToTrackOptions.minThresholdPerfToSaveFiles));
                #if the topN constraint is not active, that means the 
                #minThreshold constraint was active and satisfied...therefore,
                #save.
                if (savedFilesTracker.topNtoSave is None):
                    saveFiles=True;
                else: #otherwise, ensure the topN constraint is satisfied.
                    numRecords = jsonDb.jsonableRecordsHolder.getNumRecords();
                    #if there aren't even N records in the db, this will of course be one
                    #of the top N.
                    if (numRecords < savedFilesTracker.topNtoSave):
                        print("Top "+str(savedFilesTracker.topNtoSave)+" constraint"
                                +" satisfied as there are only "+str(numRecords)+" in the db")
                        saveFiles = True; 
                    else:
                        #otherwise, get the nth record and compare perf with it
                        nthRecord = (jsonDb.jsonableRecordsHolder
                                    .getIthSortedRecord(savedFilesTracker.topNtoSave-1))
                        nthRecordPerf = nthRecord.getField(perfToTrackOptions.perfAttrName); 
                        #if better than nth record, delete files of nth record and evict from dict
                        if (util.isBetter(perf, nthRecordPerf, perfToTrackOptions.isLargerBetter)):
                            print("Top "+str(savedFilesTracker.topNtoSave)+" constraint satisfied; "
                                    +"Nth record (record no. "+str(nthRecord.getRecordNo())
                                    +" had perf "+str(nthRecordPerf)+" and this one ("+str(prospectiveRecordNumber)
                                    +") had perf "+str(perf))
                            saveFiles=True;
                            filesToEvict = nthRecord.getField(RunTrackerRecordFields.savedFiles, noneIfAbsent=True); 
                            if (filesToEvict is None):
                                print("\n***\nWARNING: No files to evict found for ousted Nth record "
                                        +str(nthRecord.getRecordNo())+"\n***");
                            else:
                                for aFile in filesToEvict:
                                    print("Removing:",aFile);
                                    if os.path.exists(aFile)==False:
                                        print("\n***\nWARNING: I'm supposed to delete "
                                            +str(aFile)+" but it does not exist\n***");
                                    else: 
                                        os.remove(aFile);  
                                nthRecord.removeField(RunTrackerRecordFields.savedFiles);
        #if have decided not to save these files, delete them.
        if (not saveFiles):
            for aFile in savedFilesTracker.currentFiles:
                print("Removing:",aFile)
                os.remove(aFile);
        else:
            record.setField(RunTrackerRecordFields.savedFiles, savedFilesTracker.currentFiles);
    return callback;

PerfToTrackOptions = namedtuple("PerfToTrackOptions", ["perfAttrName", "isLargerBetter", "thresholdPerfToEmailAt", "minThresholdPerfToSaveFiles"]);
class SavedFilesTracker(object):
    def __init__(self, bestFileNameGivenCurrentFile, currentFiles, topNtoSave):
        self.bestFileNameGivenCurrentFile = bestFileNameGivenCurrentFile;
        self.currentFiles = currentFiles;
        self.topNtoSave = topNtoSave;

def getJsonDbFactory(emailOptions, perfToTrackOptions, JsonableRecordClass, savedFilesTracker):
    """
        Returns a json db factory that keeps track of the best of some
            attribute and also maintains records in sorted order
            of that attribute.
        savedFilesTracker is an instance of SavedFilesTracker; keeps
            track of the old best model files and the current model
            files. Will clear out old files if current files are
            the new best, otherwise will clear out the current
            files unless minThresholdPerfToSaveFiles is not None
    """
    keyFunc = lambda x: ((-1 if perfToTrackOptions.isLargerBetter else 1)*getattr(x,perfToTrackOptions.perfAttrName))
    JsonableRecordsHolderClass = jsondb.getSortedJsonableRecordsHolderClass(keyFunc=keyFunc); 
    #the metadata callbacks are: print if there's a new best, and also save
    #the best performing model.
    metadataCallbacks = [getPrintIfNewBestCallback()];
    if emailOptions is not None and emailOptions.emailMode in [EmailModes.allEmails, EmailModes.errorsAndNewBest]:
        metadataCallbacks.append(getEmailIfNewBestCallback(emailOptions, perfToTrackOptions));
    callbacks_beforeAdd = [ renameFilesWithRecordNumberCallback(savedFilesTracker)
                            , getSaveBestFilesCallback(perfToTrackOptions, savedFilesTracker)
                            , getSaveSomeFilesCallback(perfToTrackOptions, savedFilesTracker)];
    callbacks_afterAdd = [getPrintAddedRecordCallback()]
    if (emailOptions is not None and emailOptions.emailMode in [EmailModes.allEmails]):
        callbacks_afterAdd.append(getEmailRecordAddedCallback(emailOptions)); 

    MetadataClass = jsondb.getUpdateValsMetadataClass(
                        [jsondb.MetadataUpdateInfo(
                            metadataAttrName=perfToTrackOptions.perfAttrName
                            ,recordAttrName=perfToTrackOptions.perfAttrName
                            ,updateFunc=getBestUpdateFunc(
                                isLargerBetter=perfToTrackOptions.isLargerBetter
                                ,metadataCallbacks=metadataCallbacks)
                            ,initVal=None)
                        ,jsondb.NumRecordsMetadataUpdateInfo]
                        ,[RunTrackerMetadataFields.bestPerfSavedFiles]); 
    jsonDbFactory = jsondb.JsonDb.getFactory(JsonableRecordClass=JsonableRecordClass
                            ,JsonableRecordsHolderClass=JsonableRecordsHolderClass
                            ,MetadataClass=MetadataClass
                            ,callbacks_beforeAdd=callbacks_beforeAdd
                            ,callbacks_afterAdd=callbacks_afterAdd); 
    return jsonDbFactory; 

RunTrackerRecordFields = util.enum(savedFiles="savedFiles");
RunTrackerMetadataFields = util.enum(bestPerfSavedFiles="bestPerfSavedFiles");

EmailModes = util.enum(noEmails="noEmails", onlyErrorEmails="onlyErrorEmails", errorsAndNewBest="errorsAndNewBest", allEmails="allEmails"); 
def addRunTrackerArgumentsToParser(parser):
    parser.add_argument("--emails", nargs="+", required=True, help="Provide a dummy val if don't want emails");
    parser.add_argument("--emailMode", choices=EmailModes.vals, default=EmailModes.errorsAndNewBest);
    parser.add_argument("--jobName", help="Used to create email subjects and log files");
    parser.add_argument("--logFile");
    parser.add_argument("--jsonDbFile", required=True, help="Used to save the records");
    parser.add_argument("--thresholdPerfToEmailAt", type=float, help="New Best emails only sent above this threshold")
    parser.add_argument("--minThresholdPerfToSaveFiles", type=float, help="Only files above this threshold are saved");
    parser.add_argument("--topNtoSave", default=100, type=int, help="Keep top N performing models");

def runTrackerArguments_fillDefaults(options):
    coreJsonDb = fp.getCoreFileName(options.jsonDbFile); 
    if (options.logFile is None):
        options.logFile = fp.getFileNameParts(options.jsonDbFile)\
                            .getFilePathWithTransformation(lambda x: "log_"+x, extension=".txt");
    if (options.jobName is None):
        options.jobName = coreJsonDb; 

