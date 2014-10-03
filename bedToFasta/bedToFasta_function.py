
#!/usr/bin/python
import sys;
import gzip;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;
import parallelProcessing as pp;
import parallelisingFunction as pf;

def bedToFasta(inputBedFile, finalOutputFile, faSequencesDir):

	tempOutputDir = util.getTempDir();
	filePathMinusExtensionFromChromosome = lambda chrom: tempOutputDir + "/" + chrom+"_"+fp.getFileNameParts(inputBedFile).coreFileName;
	pathToInputFaFromChrom = lambda chrom : faSequencesDir+"/"+chrom+".fa";
	bedFilePathFromChromosome = lambda chrom: filePathMinusExtensionFromChromosome(chrom)+".bed"; 
	fastaFilePathFromChromosome = lambda chrom: filePathMinusExtensionFromChromosome(chrom)+".fasta";

	def bedtoolsCommandFromChromosome(chrom): #produces the bedtools command given the chromosome
		return "bedtools getfasta -tab -fi "+pathToInputFaFromChrom(chrom)+" -bed "+bedFilePathFromChromosome(chrom)+ " -fo "+fastaFilePathFromChromosome(chrom);
	
	#step 1: split lines into other files based on 'filter variables' extracted from each line.
	chromosomes = fp.splitLinesIntoOtherFiles(
		fp.getFileHandle(inputBedFile) #the file handle that is the source of the lines
		, util.chainFunctions(fp.trimNewline,fp.splitByTabs) #preprocessing step to be performed on each line
		, fp.lambdaMaker_getAtPosition(0) #filter variable from preprocessed line; in bed files, chromosome is at position 0
		, bedFilePathFromChromosome #function to produce output file path from filter variable
	);
	
	#step 2: kick of parallel threads to run bedtools
	pp.ParalleliserFactory(pp.ParalleliserInfo( #wrapper class - put in place for possible future extensibility.
		pf.ThreadBasedParalleliser(
			#function to execute on each input, in this case each chromosome
			pf.lambdaProducer_executeAsSystemCall(
				bedtoolsCommandFromChromosome #produces the bedtools command give the chromosome
			)
		))).getParalleliser(chromosomes).execute();
	
	#concatenate files using cat
	fp.concatenateFiles(finalOutputFile, [fastaFilePathFromChromosome(chrom) for chrom in chromosomes]);

