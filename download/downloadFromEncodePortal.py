#!/usr/bin/env python
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import argparse;
import re;

def getDownloadCommand(link, cookiesFile, outputFile):
    cmd = "wget --load-cookies="+cookiesFile+" --output-document="+outputFile+" "+link;
    return cmd;

def doDownload(link, cookiesFile, outputFile):
    cmd = getDownloadCommand(link, cookiesFile, outputFile);
    print(cmd);
#    os.system(getDownloadCommand(link, cookiesFile, outputFile)); 
    
def getFileFromLink(link):
    """
        Extract the actual file from the end of the link
    """
    p = re.compile(r"^(.*/)?([^/]+)$");
    m = p.search(link);
    return m.group(2);

def downloadFromEncodePortal(options):
    fileWithLinks = options.fileWithLinks; 
    linksArr = fp.readRowsIntoArr(fp.getFileHandle(fileWithLinks)); 
    outputFileNames = [getFileFromLink(x) for x in linksArr];
    for link, outputFileName in zip(linksArr, outputFileNames):
        doDownload(link, options.cookiesFile, outputFileName);
      

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--fileWithLinks", required=True);
    parser.add_argument("--cookiesFile", required=True);
    options = parser.parse_args();
    downloadFromEncodePortal(options);
