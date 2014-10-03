#!/usr/bin/python
import sys;
sys.path.insert(0,"/home/avanti/av_scripts");
import util;
import argparse;

def main():
	parser = argparse.ArgumentParser(description="Generate a qsub file");
	parser.add_argument('--shPath', help="The path of the qsub .sh file");
	parser.add_argument('--email');
	parser.add_argument('--cores');
	parser.add_argument('--mem');
	parser.add_argument('--runtime'); 
	parser.add_argument('args', nargs=argparse.REMAINDER, help="The command that you are actuall submitting through the qsub file");
	args = parser.parse_args();
	if (len(args.args) < 1):
		parser.print_help();
		sys.exit(1);
	writeQsubFile(args);

def writeQsubFile(args):
	header = uq.getDefaultHeaderBasedOnFilePath(args.shPath, args.email);
	header.numCores = args.cores;
	header.maxMem = args.mem;
	header.maxRuntime = args.runtime;
	uq.writeQsubFile(args.shPath, header, " ".join(args.args));

main(); 
