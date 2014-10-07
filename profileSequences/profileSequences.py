import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;


def main():
	parser = argparse.ArgumentParser(description="Profiles the sequences");
	parser.add_argument('--hasTitle',action="store_true");
	parser.add_argument('--groupByColIndex',type=int);
	parser.add_argument('--sequencesColIndex',type=int);
	parser.add_argument('--baseCount', action='store_true');
	parser.add_argument('--cgContent', action='store_true');
	parser.add_argument('--lowercase', action='store_true');
	parser.add_argument('--kmer', type=int);
	args = parser.parse_args();
main();


