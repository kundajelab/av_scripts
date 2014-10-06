import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import fishersExact_function;


class CountProfiler:
	counts = {};
	def __init__(self,keysGenerator):
		self.keysGenerator = keysGenerator;
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
	def __init__(self,keysGenerator):
		self.keysGenerator = keysGenerator;
	def getCountProfiler():
		return CountProfiler(keysGenerator);
	
class LetterByLetterCountProfilerFactory(CountProfilerFactory):
	counts = {};
	def __init__(self,letterToKey):
		def keysGenerator():
			for letter in sequence:
				yield letterToKey(letter);
		super(LetterByLetterCountProfilerFactory,self).__init__(keysGenerator);

#TODO: implement more efficient rolling window if perf is issue
class KmerCountProfilerFactory(CountProfilerFactory):
	def __init__(self,stringPreprocess,kmerLength):
		def keysGenerator():
			sequence = stringPreprocess(sequence);
			#not the best rolling window but eh:
			for i in range(0,len(sequence)-kmerLength):
				yield sequence[i:i+kmerLength];
		super(KmerProfilerFactory,self).__init__(keysGenerator);

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
		







