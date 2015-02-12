#!/usr/bin/env python
import os;
import time;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import util;
import argparse;

def launchScriptWhenPidCompletes(options):
    while(util.check_pid(options.pid)):
        print "Alive";
        time.sleep(5);

    os.system("sh "+options.script);

if __name__ == "__main__":
    parser = argparser.ArgumentParser();
    parser.add_argument("--script", required=True);
    parser.add_argument("--pid", type=int, required=True);
    launchScriptWhenPidCompletes(parser.parse_args());
