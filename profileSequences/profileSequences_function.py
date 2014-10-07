import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fishersExact_function;
import fileProcessing as fp;
import util;

def profileInputFile(inputFileHandle
	, countProfilerFactories
	, categoryFromInput
	, sequenceFromInput
	, significanceThreshold=0.01
	, preprocessing=None
	, filterFunction=None
	, transformation=lambda x: x
	, progressUpdates=None
	, ignoreInputTitle=False):
	#init map of count profiler name to map of category-->count
	profilerName_to_categoryToCountMaps = {};	
	def action(input,i): #the input is the value of the line after preprocess, filter and transformation
		category = categoryFromInput(input);
		sequence = sequenceFromInput(input);
		for countProfilerFactory in countProfilerFactories:
			if (countProfilerFactory.profilerName not in profilerName_to_categoryToCountMaps):
				profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName] = {}
			if (category not in profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName]):
				profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName][category] = countProfilerFactory.getCountProfiler();
			profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName][category].process(sequence);

	fp.performActionOnEachLineOfFile(
		inputFileHandle
		,action
		,preprocessing=preprocessing
		,filterFunction=filterFunction
		,transformation=transformation
		,ignoreInputTitle=ignoreInputTitle
		,progressUpdates=progressUpdates
	);		

	significantDifferences = {};
	for profilerName in profilerName_to_categoryToCountMaps:
		categoryCountMap = profilerName_to_categoryToCountMaps[profilerName];
		significantDifferences[profilerName] = profileCountDifferences(categoryCountMap,significanceThreshold);
	return significantDifferences;	

class CountProfiler:
	def __init__(self,keysGenerator,profilerName):
		self.counts = {};
		self.keysGenerator = keysGenerator;
		self.profilerName = profilerName;
	def process(self,sequence):
		for key in self.keysGenerator(sequence):
			if (key not in self.counts):
				self.counts[key] = 0;
			self.counts[key] += 1;
	def normalise(self):
		total = 0;
		for aKey in self.counts:
			total += self.counts[aKey];
		self.total = total;
		self.normalisedCounts = {};
		for aKey in self.counts:
			self.normalisedCounts[aKey] = float(self.counts[aKey])/total;
		return self.normalisedCounts;

class CountProfilerFactory(object):
	def __init__(self,keysGenerator,profilerName):
		self.keysGenerator = keysGenerator;
		self.profilerName = profilerName;
	def getCountProfiler(self):
		return CountProfiler(self.keysGenerator,self.profilerName);
	
class LetterByLetterCountProfilerFactory(CountProfilerFactory):
	def __init__(self,letterToKey,profilerName):
		def keysGenerator(sequence):
			for letter in sequence:
				yield letterToKey(letter);
		super(self.__class__,self).__init__(keysGenerator,profilerName);

def getLowercaseCountProfilerFactory():
	lowercaseAlphabet = ['a','c','g','t']
	uppercaseAlphabet = ['A','C','G','T']
	def letterToKey(x):
		if (x in lowercaseAlphabet):
			return 'acgt';
		if (x in uppercaseAlphabet):
			return 'ACGT';
		if (x == 'N'):
			return 'N';
		raise Exception("Unexpected dna input: "+x);
	return LetterByLetterCountProfilerFactory(letterToKey, 'LowercaseCount');

def getGcCountProfilerFactory():
	cgArr = ['c','g','C','G'];
	atArr = ['a','t','A','T'];
	def letterToKey(x):
		if (x in cgArr):
			return 'GC';
		if (x in atArr):
			return 'AT';
		if (x == 'N'):
			return 'N';
		raise Exception("Unexpected dna input: "+x);
	return LetterByLetterCountProfilerFactory(letterToKey, 'GC-content');

def getBaseCountProfilerFactory():
	return LetterByLetterCountProfilerFactory(lambda x: x.upper(), 'BaseCount');


#TODO: implement more efficient rolling window if perf is issue
class KmerCountProfilerFactory(CountProfilerFactory):
	def __init__(self,stringPreprocess,kmerLength):
		def keysGenerator(sequence):
			sequence = stringPreprocess(sequence);
			#not the best rolling window but eh:
			for i in range(0,len(sequence)-kmerLength):
				yield sequence[i:i+kmerLength];
		super(KmerCountProfilerFactory,self).__init__(keysGenerator,str(kmerLength)+"-mer");

def profileCountDifferences(mapOfCategoryToCountProfiler,significanceThreshold=0.01):
	significantResults = [];
	keyTotals = {};
	grandTotal = 0;
	for category in mapOfCategoryToCountProfiler:
		mapOfCategoryToCountProfiler[category].normalise();
		counts = mapOfCategoryToCountProfiler[category].counts;
		grandTotal += mapOfCategoryToCountProfiler[category].total;
		for key in counts:
			if key not in keyTotals:
				keyTotals[key] = 0;
			keyTotals[key] += counts[key];
	#performing the hypgeo test:
	for category in mapOfCategoryToCountProfiler:
		counts = mapOfCategoryToCountProfiler[category].counts;
		for key in counts:
			special = keyTotals[key];
			picked = mapOfCategoryToCountProfiler[category].total;
			specialPicked = counts[key];
			hypGeoPVal = fishersExact_function.hypGeo_cumEqualOrMoreOverlap(grandTotal,special,picked,specialPicked);
			if (hypGeoPVal <= significanceThreshold):
				significantResults.append(SignificantResults(grandTotal,special,picked,specialPicked,hypGeoPVal,key,category));
	return significantResults;

class SignificantResults:
	def __init__(self,total,special,picked,specialPicked,pval,specialName="special",pickedName="picked"):
		self.total = total;
		self.special = special;
		self.picked = picked;
		self.specialPicked = specialPicked;
		self.pval = pval;
		self.specialName = specialName;
		self.pickedName = pickedName;
	def __str__(self):
		return ("pval: "+str(self.pval)
			+", "+self.specialName+": "+str(self.special)
			+", "+self.pickedName+": "+str(self.picked)
			+", both: "+str(self.specialPicked)
			+", total: "+str(self.total)); 		







