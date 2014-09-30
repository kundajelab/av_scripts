###Done checkers

class DoneStateEnum:
	SUCCESS = "SUCCESS";
	ERROR = "ERROR";

#Interface DoneInfo:
	#DoneStateEnum doneStatus
	#String message (to be used to raise exception if doneStatus is ERROR)

#Interface DoneChecker:
	#Boolean isDone()
	#DoneInfo getStatus() 

class DoneChecker_checkIfFileExists:
	def __init__(self,filePath):
		self.filePath = filePath;
	def isDone(self):
		#return true if file exists
	def getStatus(self):
		if (!self.isDone()):
			print "Can't call getStatus unless doneChecker isDone()";
			raise;
		#read the json in the donefile and return the corresponding info.
		#try to have that json include a "message" field!

