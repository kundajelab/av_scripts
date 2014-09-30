import doneChecker as dc;
import multiprocessing;
import os;
import sys;
sys.path.insert(0,"..");
import util;

#Interface ParallelisingFunction:
	#DoneInfo execute(Object input)

class ThreadBasedParalleliser: #implements ParallelisingFunction, done 'done' checks based on whether the thread is alive.
	def __init__(self, funcToExecute):
		self.funcToExecute = funcToExecute;
	def execute(self,theInput):
		theThread = multiprocessing.Process(target=lambda : self.funcToExecute(theInput));
		theThread.start()
		return dc.DoneChecker_threadJoiner(theThread);  
	



#given a function that returns the string command to execute from the input,
#produces a function that actually executes the command.
def lambdaProducer_executeAsSystemCall(commandFromInput):
	return lambda x: util.executeAsSystemCall(commandFromInput(x));

