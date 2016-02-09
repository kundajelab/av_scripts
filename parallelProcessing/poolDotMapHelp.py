from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR"
                    " to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;

#to be continued
