import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);


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
