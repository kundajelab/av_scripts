###Done checkers

class DoneStateEnum:
	SUCCESS = "SUCCESS";
	ERROR = "ERROR";

#Interface DoneInfo:
	#DoneStateEnum doneStatus
	#String message (to be used to raise exception if doneStatus is ERROR)
class DoneInfo:
	def __init__(self, doneStatus, message):
		this.doneStatus = doneStatus;
		this.message = message;

#Interface DoneChecker:
	#Boolean isDone()
	#DoneInfo getStatus() 

class DoneChecker:
	def getStatus(self):
		if (!self.isDone()):
			print "Can't call getStatus unless doneChecker isDone()";
			raise;

class DoneChecker_checkIfFileExists(DoneChecker):
	def __init__(self,filePath):
		self.filePath = filePath;
	def isDone(self):
		#return true if file exists
	def getStatus(self):
		super(DoneChecker_checkIfFileExists, self).getStatus();
		#read the json in the donefile and return the corresponding info.
		#try to have that json include a "message" field!

class DoneChecker_threadJoiner:
	def __init__(self, theThread):
		self.theThread = theThread;
	def isDone(self):
		isAlive = theThread.isAlive();
		if (isAlive):
			return False;
		else:
			theThread.join();
			return True;
	def getStatus(self):
		super(DoneChecker_checkIfFileExists, self).getStatus();
		return DoneInfo(DoneStatus.SUCCESS, "The thread finished so success I guess.");

