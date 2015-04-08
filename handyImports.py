import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
import sys;
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import parallelProcessing as pp;
import util_qsub as uq;
