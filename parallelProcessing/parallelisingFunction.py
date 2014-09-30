import doneChecker as dc;
import thread;
import os;

#Interface ParallelisingFunction:
	#DoneInfo execute(Object input)

class ThreadBasedParalleliser: #implements ParallelisingFunction
	def __init__(self, funcToExecute, doneInfoProducer):
		this.funcToExecute = funcToExecute;
		this.doneInfoProducer = doneInfoProducer;
	def execute(self,theInput):
		thread.start_new_thread(funcToExecute, (theInput));
		return doneInfoProducer(theInput);

class ExecuteAsSystemCall:
	def __init__(self, commandToExecute):
		this.commandToExecute = commandToExecute;
	def execute(self):
		print "Executing: "+this.commandToExecute;
		os.system(commandToExecute);

#given a function that returns the command to execute from the input,
#produces a function that actually executes the command.
def lambdaProducer_executeAsSystemCall(commandFromInput):
	return lambda x: ExecuteAsSystemCall(commandFromInput(x)).execute();


