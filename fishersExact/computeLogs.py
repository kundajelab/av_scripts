#!/usr/bin/python
import math;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import computeLogs_function;

def main():
	parser = argparse.ArgumentParser(description="Generate a file with the factorials");
	parser.add_argument('--outputFile', help="If not specified, will generate output file logFactorial_[upTo].txt");
	parser.add_argument('--upTo', type=int, default=30000, help="Up till this value will be printed");
	args = parser.parse_args();
	computeLogs_function.writeLogFactorialFile(args);
main();

