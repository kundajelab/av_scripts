###Done checkers
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;

DONE_STATE = util.enum(success="success", error="error");

class DoneInfo:
	def __init__(self, doneStatus, message):
		"""
            doneStatus: instance of DONE_STATE
            message: string
        """
        self.doneStatus = doneStatus;
		self.message = message;

class DoneChecker:
    def isDone(self):
        """
            return: boolean indicating whether the job is done
        """
        raise NotImplementedError();
	def getStatus(self):
        """
            returns a DONE_STATE; checks that isDone() is true
        """
		if (self.isDone()==False):
			raise Exception("Can't call getStatus unless doneChecker isDone()");
        return self._getStatus();
    def _getStatus(self):
        """
            returns instance of DONE_STATE
        """
        raise NotImplementedError();

class DoneChecker_threadJoiner:
    """
        calls is_alive() on a thread, and when is_alive is false, joins the thread.
    """
	def __init__(self, theThread):
		self.theThread = theThread;
	def isDone(self):
		if (self.theThread.is_alive()):
			return False;
		else:
			self.theThread.join();
			return True;
	def _getStatus(self):
		return DoneInfo(DONE_STATE.success, "The thread finished so success I guess.");

class DoneChecker_checkIfFileExists(DoneChecker):
	def __init__(self,filePath):
		self.filePath = filePath;
	def isDone(self):
		return os.path.isfile(filePath);
	def _getStatus(self):
		#read the json in the donefile and return the corresponding info.
		#try to have that json include a "message" field!
		raise NotImplementedError();

