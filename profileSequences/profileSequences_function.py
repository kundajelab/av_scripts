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

class profileInputFile(inputFileHandle
	, countProfilerFactories
	, significanceThreshold = 0.01
	, preprocessing = None
	, filterFunction = None
	, transformation = lambda x: x
	, categoryFromInput
	, sequenceFromInput
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
	


class CountProfiler:
	counts = {};
	def __init__(self,keysGenerator,profilerName):
		self.keysGenerator = keysGenerator;
		self.profilerName = profilerName;
	def process(self,sequence):
		for key in self.keysGenerator:
			if (key not in self.counts):
				self.counts[key] = 0;
			self.counts[key] += 1;
	def normalise():
		total = 0;
		for aKey in self.counts:
			total += self.counts[aKey];
		self.total = total;
		self.normalisedCounts = {};
		for aKey in self.counts:
			self.normalisedCounts[aKey] = float(self.counts[aKey])/total;
		return self.normalisedCounts;

class CountProfilerFactory:
	def __init__(self,keysGenerator,profilerName):
		self.keysGenerator = keysGenerator;
		self.profilerName = profilerName;
	def getCountProfiler():
		return CountProfiler(self.keysGenerator,self.profilerName);
	
class LetterByLetterCountProfilerFactory(CountProfilerFactory):
	counts = {};
	def __init__(self,letterToKey,profilerName):
		def keysGenerator():
			for letter in sequence:
				yield letterToKey(letter);
		super(LetterByLetterCountProfilerFactory,self).__init__(keysGenerator,profilerName);

#TODO: implement more efficient rolling window if perf is issue
class KmerCountProfilerFactory(CountProfilerFactory):
	def __init__(self,stringPreprocess,kmerLength):
		def keysGenerator():
			sequence = stringPreprocess(sequence);
			#not the best rolling window but eh:
			for i in range(0,len(sequence)-kmerLength):
				yield sequence[i:i+kmerLength];
		super(KmerProfilerFactory,self).__init__(keysGenerator,str(kmerLength)+"-mer");

def profileKmers(mapOfCategoryToCountProfiler,significanceThreshold=0.01):
	significantResults = [];
	keyTotals = {};
	grandTotal = 0;
	for category in mapOfCategoryToCountProfiler:
		mapOfCategoryToCountProfiler[category].normalise();
		counts = mapOfCategoryToCountProfiler[category].counts;
		grandTotal += counts.total;
		for key in counts:
			if key not in keyTotals:
				keyTotals[key] = 0;
			keyTotals[key] += counts[key];
	#performing the hypgeo test:
	for category in mapOfCategoryToCountProfiler:
		counts = mapOfCategoryToCountProfiler[category].counts;
		for key in counts:
			special = keyTotals[key];
			picked = counts.total;
			specialPicked = counts[key];
			hypGeoPVal = fishersExact_function.hypGeo_cumEqualOrMoreOverlap(grandTotal,special,picked,specialPicked);
			if (hypGeoPVal < significanceThreshold):
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
		







