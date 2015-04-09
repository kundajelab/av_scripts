import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import fileProcessing as fp;
import argparse;

def issueDownloadCommand(link, cookieFile, 

def downloadFromEncodePortal(options):
    fileWithLinks = options.fileWithLinks; 
    linksArr = fp.readRowsIntoArr(fp.getFileHandle(fileWithLinks)); 

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--fileWithLinks", required=True);
    parser.add_argument("--cookiesFile", required=True);
    options = parser.parse_args();
    downloadFromEncodePortal(options);
