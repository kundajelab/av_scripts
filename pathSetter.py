import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
sys.path.insert(0, scriptsDir);
sys.path.insert(0, scriptsDir+"/bedToFasta");
sys.path.insert(0, scriptsDir+"/externalLibs");
sys.path.insert(0, scriptsDir+"/parallelProcessing");
sys.path.insert(0, scriptsDir+"/qsub");
sys.path.insert(0, scriptsDir+"/fileProcessing");
