#!/srv/gs1/software/python/python-2.7/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import profileSequences_function;
import util;

def main():
	parser = argparse.ArgumentParser(description="Profiles the sequences");
	parser.add_argument('inputFile');
	parser.add_argument('--outputFile',help="If not specified, name will be 'profiledDifferences_inputFile'");
	parser.add_argument('--significanceThreshold',type=float,default=0.01);
	parser.add_argument('--progressUpdates',type=int);
	parser.add_argument('--hasNoTitle',action="store_true");
	parser.add_argument('--groupByColIndex',type=int);
	parser.add_argument('--sequencesColIndex',type=int,required=True);
	parser.add_argument('--baseCount', action='store_true');
	parser.add_argument('--gcContent', action='store_true');
	parser.add_argument('--lowercase', action='store_true');
	parser.add_argument('--kmer', type=int);
	args = parser.parse_args();
	profileSequences(args);	

def profileSequences(args):
	countProfilerFactories = [];
	if (args.kmer is not None):
		countProfilerFactories.append(profileSequences_function.KmerCountProfilerFactory(lambda x: x.upper(), args.kmer));
	if (args.lowercase):
		countProfilerFactories.append(profileSequences_function.getLowercaseCountProfilerFactory());
	if (args.gcContent):
		countProfilerFactories.append(profileSequences_function.getGcCountProfilerFactory());
	if (args.baseCount):
		countProfilerFactories.append(profileSequences_function.getBaseCountProfilerFactory());

	significantDifferences = profileSequences_function.profileInputFile(
		fp.getFileHandle(args.inputFile)
		, countProfilerFactories
		, categoryFromInput=((lambda x: x[args.groupByColIndex]) if (args.groupByColIndex is not None) else (lambda x: "defaultCategory"))
		, sequenceFromInput=(lambda x: x[args.sequencesColIndex])
		, significanceThreshold=args.significanceThreshold
		, preprocessing = util.chainFunctions(fp.trimNewline,fp.splitByTabs)
		, progressUpdates=args.progressUpdates
		, ignoreInputTitle=(not (args.hasNoTitle))
	);
	
	toPrint = "";
	for category in significantDifferences:
		toPrint = toPrint + "-----\n" + category + ":\n-----\n";
		toPrint = toPrint + "\n".join([str(x) for x in significantDifferences[category]])+"\n";
	
	if (args.outputFile is None):
		args.outputFile = fp.getFileNameParts(args.inputFile).getFilePathWithTransformation(lambda x: 'profiledDifferences_'+x, '.txt');
		
	fp.writeToFile(args.outputFile, toPrint);
	

main();

