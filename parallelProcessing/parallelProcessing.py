import parallelisingFunction as pf;
import time;

class ParalleliserInfo:
	#parallelisingFunction should, when called on an input, return a doneChecker
	def __init__(self, parallelisingFunction):
		self.parallelisingFunction = parallelisingFunction;

class ParalleliserFactory:
	def __init__(self, paralleliserInfo):
		this.paralleliserInfo = paralleliserInfo;
	def getParalleliser(self, inputs):
		return Paralleliser(inputs, paralleliserInfo);

class Paralleliser:
	doneCheckers = [];
	paralleliserState = ParalleliserState.NOT_STARTED;
	
	def __init__(self, inputs, paralleliserInfo):
		self.inputs = inputs;
		self.paralleliserInfo;

	def execute(self, waitInterval=1): #wait interval is in seconds	
		paralleliserState = ParalleliserState.STARTED
		for anInput in inputs:
			doneCheckers.append(paralleliserInfo.parallelisingFunction(anInput))
		
		isDone = False;
		while (!isDone):
			time.sleep(waitInterval);
		paralleliserState = ParalleliserState.DONE;
	
	def isDone(self): #for private use
		for doneChecker in doneCheckers:
			if (doneChecker == False):
				return False;
		return True;	


	class ParalleliserState:
		NOT_STARTED = "NOT_STARTED";		
		STARTED = "STARTED";
		DONE = "DONE";
