av_scripts
==========

Set the environment variable UTIL_SCRIPTS_DIR to point to wherever you clone this repo. Then, in order to set the paths up, import pathSetter.py. 
You can use the following snippet:

import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;

Please ping avanti@stanford.edu if you are planning to use any of these scripts - that way, I can avoid making breaking changes to stuff that other people are using, and can make sure everything is in good working condition! And let me know if something does not work!
