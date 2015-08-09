import time;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import multiprocessing;
import parallelProcessKickerOffer as ppko;

class ParalleliserInfo:
    """
        contains all the information necessary to do the parallelisation.
    """
    def __init__(self, functionToExecute, collectReturnValues=False, waitInterval=5):
        """
            collectReturnValues: boolean indicating whether you want to collect return
                values after the function is executed
        """
        self.queue = multiprocessing.Queue() if collectReturnValues else None;
        self.parallelProcessKickerOffer = ppko.ParallelProcessKickerOffer_Multiprocessing(functionToExecute, returnQueue=self.queue); 
        self.waitInterval = waitInterval;

class ParalleliserFactory: #wow this class has minimal functionality why do I even use it?
    def __init__(self, paralleliserInfo):
        self.paralleliserInfo = paralleliserInfo;
    def getParalleliser(self, inputs):
        """
            inputs: an array of FunctionInputs
        """
        return Paralleliser(inputs, self.paralleliserInfo);

ParalleliserState = util.enum(
    NOT_STARTED = "NOT_STARTED"    
    , STARTED = "STARTED"
    , DONE = "DONE");

class FunctionInputs(object):
    """
        Stores the inputs that will be used to call some function
    """
    def __init__(self, args=[], kwargs={}):
        self.args = args;
        self.kwargs = kwargs;

class Paralleliser(object):
    """
        takes an instance of paralleliserInfo (which contains info on how to kick off the jobs) and
        a series of inputs, and executes the jobs in parallel.
    """    
    def __init__(self, inputs, paralleliserInfo):
        """
            inputs: an array of FunctionInputs
        """
        self.doneCheckers = [];
        self.paralleliserState = ParalleliserState.NOT_STARTED;
        self.inputs = inputs;
        self.paralleliserInfo = paralleliserInfo;

    def execute(self): #wait interval is in seconds    
        if (self.paralleliserState != ParalleliserState.NOT_STARTED):
            raise RuntimeError("Paralleliser was already started!");
        self.paralleliserState = ParalleliserState.STARTED
        for anInput in self.inputs:
            self.doneCheckers.append(self.paralleliserInfo.parallelProcessKickerOffer.execute(*anInput.args, **anInput.kwargs))    
        isDone = False;
        numRunningJobs = self._numRunningJobs();
        #while (numRunningJobs != 0):
        #    time.sleep(self.paralleliserInfo.waitInterval); 
        #    numRunningJobs = self._numRunningJobs();
        #    print("Sleeping; number of running jobs is "+str(numRunningJobs));
        self.paralleliserState = ParalleliserState.DONE;
        return self.paralleliserInfo.queue;
   
    def finish(self):
        for doneChecker in self.doneCheckers:
            doneChecker.finish();
     
    def _numRunningJobs(self): #for private use
        numRunningJobs = 0;
        for doneChecker in self.doneCheckers:
            if (doneChecker.isDone() != True):
                numRunningJobs += 1;
        return numRunningJobs;    

    

