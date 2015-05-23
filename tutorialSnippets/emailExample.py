#!/usr/bin/env python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;

util.sendEmail("anna.borja@couchsurfing.com", "anna.borja@couchsurfing.com", "You've got male!", 
                "I realised my explanation was a little incomplete, so I wrote a script at /home/avanti/demo/emailExample.py that has the bare essentials.\n\n"
                +"If you just set the environment variable UTIL_SCRIPTS_DIR to point to /home/pgreens/av_scripts, it should work.\n\nP.S. now you can do email spoofing and scare people.");
