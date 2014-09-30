import doneChecker as dc;
import threading;
import os;
import sys;
sys.path.insert(0,"..");
import util;

#Interface ParallelisingFunction:
	#DoneInfo execute(Object input)

#a thread that just executes the supplied function
class FunctionExecutingThread(threading.Thread):
	def __init__(self, functionToExecute):
		threading.Thread.__init__(self);
		self.functionToExecute = functionToExecute;
	def run(self):
		self.functionToExecute();

class ThreadBasedParalleliser: #implements ParallelisingFunction, done 'done' checks based on whether the thread is alive.
	def __init__(self, funcToExecute):
		self.funcToExecute = funcToExecute;
	def execute(self,theInput):
		theThread = FunctionExecutingThread(lambda : self.funcToExecute(theInput));
		theThread.start()
		return dc.DoneChecker_threadJoiner(theThread);  
	



#given a function that returns the string command to execute from the input,
#produces a function that actually executes the command.
def lambdaProducer_executeAsSystemCall(commandFromInput):
	return lambda x: util.executeAsSystemCall(commandFromInput(x));

