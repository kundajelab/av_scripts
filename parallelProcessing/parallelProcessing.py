import parallelisingFunction as pf;
import time;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;

class ParalleliserInfo:
	#parallelisingFunction should, when called on an input, return a doneChecker
	def __init__(self, parallelisingFunction):
		self.parallelisingFunction = parallelisingFunction;

class ParalleliserFactory:
	def __init__(self, paralleliserInfo):
		self.paralleliserInfo = paralleliserInfo;
	def getParalleliser(self, inputs):
		return Paralleliser(inputs, self.paralleliserInfo);

ParalleliserState = util.enum(
	NOT_STARTED = "NOT_STARTED"	
	, STARTED = "STARTED"
	, DONE = "DONE");

class Paralleliser:	
	def __init__(self, inputs, paralleliserInfo):
		self.doneCheckers = [];
		self.paralleliserState = ParalleliserState.NOT_STARTED;
		self.inputs = inputs;
		self.paralleliserInfo = paralleliserInfo;

	def execute(self, waitInterval=1): #wait interval is in seconds	
		paralleliserState = ParalleliserState.STARTED
		for anInput in self.inputs:
			self.doneCheckers.append(self.paralleliserInfo.parallelisingFunction.execute(anInput))
		
		isDone = False;
		while (self.isDone() == False):
			time.sleep(waitInterval);
			"Sleeping";
		paralleliserState = ParalleliserState.DONE;
	
	def isDone(self): #for private use
		for doneChecker in self.doneCheckers:
			if (doneChecker.isDone() != True):
				return False;
		return True;	


