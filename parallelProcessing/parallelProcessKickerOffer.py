import doneChecker as dc;
import multiprocessing;
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import util;

"""
    Designed to work with ParalleliserInfo in parallelProcessing.py; PalleliserInfo
        will have an instance of AbstractParallelProcessKickerOffer which actually
        kicks off the parllel processes on the different inputs.
"""

def getFunctionWrapperToPutStuffInQueue(function, outputQueue):
    """
        Returns a wrapper function that is used to capture the returned value of the function
        and put it in a queue (Queue.Queue is thread-safe)
    """
    def wrapperFunction(*args,**kwargs):
        returnVal = function(*args,**kwargs);
        print("Return val is",returnVal);
        outputQueue.put(returnVal);
        print("successful put");
    return wrapperFunction;

class AbstractParallelProcessKickerOffer(object): 
    def __init__(self, funcToExecute, returnQueue=None):
        if (returnQueue is not None):
            print("Return queue is not none");
            funcToExecute = getFunctionWrapperToPutStuffInQueue(funcToExecute, returnQueue);
        self.funcToExecute = funcToExecute;
    def execute(self,*args,**kwargs):
        raise NotImplementedError();

class ParallelProcessKickerOffer_Multiprocessing(AbstractParallelProcessKickerOffer):
    def execute(self, *args, **kwargs):
        theThread = multiprocessing.Process(target=lambda : self.funcToExecute(*args,**kwargs));
        theThread.start()
        return dc.DoneChecker_threadAlive(theThread);  

#given a function that returns the string command to execute from the input,
#produces a function that actually executes the command.
def lambdaProducer_executeAsSystemCall(commandFromInput):
    def funcToReturn(*args,**kwargs):
        return util.executeAsSystemCall(commandFromInput(*args,**kwargs));
    return funcToReturn;
