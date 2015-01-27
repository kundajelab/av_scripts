#!/usr/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;
import argparse;

def writeFileAndEmailWhenDone(args):
    fileHandle = fp.getFileHandle(args.shPath, 'w');
    fileHandle.write(" ".join(args.args));
    fileHandle.close();
    outFile = args.shPath+".out";
    os.system("sh "+args.shPath+" >"+outFile+" 2>&1");
    util.sendEmail(args.email, 'jobRunner@stanford.edu', "Done "+args.shPath, "");
    if (args.dontRm == False):
        os.system("rm "+args.shPath);
        os.system("rm "+outFile);

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a shell script that is then launched and an email is sent when done");
    parser.add_argument('--shPath', help="The path of the .sh file. Defaults to temp.sh");
    parser.add_argument('--email', default='avanti@stanford.edu');
    parser.add_argument('args', nargs=argparse.REMAINDER, help="The command that you are actuall submitting through the shell script");
    parser.add_argument('--dontRm', action='store_true', help='Wont remove file when done');
    args = parser.parse_args();
    if (len(args.args) < 1):
        parser.print_help();
        sys.exit(1);
    if (args.shPath is None):
        args.shPath = fp.getCoreFileName(args.args[0])+".sh";
    writeFileAndEmailWhenDone(args);

