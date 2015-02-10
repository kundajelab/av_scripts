#!/usr/bin/env python
#/srv/gs1/software/python/python-2.7/bin/python
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
import stats;
import computeLogs_function;

def main():
	parser = argparse.ArgumentParser(description="Does a hypergeometric/two-proportion z-test for >= overlap");
	parser.add_argument('--total',required=True,type=int);
	parser.add_argument('--special',required=True,type=int);
	parser.add_argument('--picked',required=True,type=int);
	parser.add_argument('--specialPicked',required=True,type=int);
	args = parser.parse_args();
	print(str(stats.proportionTest(args.total,args.special,args.picked,args.specialPicked)));
main();

