import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import stats;
import fileProcessing as fp;
import util;
import profileSequences_function as ps_f;
import argparse;

#import the countProfiler function. - ps_f.CountProfiler

def main():
	parser = argparse.ArgumentParser(description="Applies naive Bayes classifier");
	parser.add_argument("--sequenceIndex", required=True);
	parser.add_argument("--categoryIndex", required=True); 

	profilerName_to_categoryToCountMaps = profileSequences_function.profileInputFile(
		fp.getFileHandle(args.inputFile)
		, countProfilerFactories
		, categoryFromInput=((lambda x: x[args.groupByColIndex]) if (args.groupByColIndex is not None) else (lambda x: "defaultCategory"))
		, sequenceFromInput=(lambda x: x[args.sequencesColIndex])
		, preprocessing = util.chainFunctions(fp.trimNewline,fp.splitByTabs)
		, progressUpdates=args.progressUpdates
		, ignoreInputTitle=(not (args.hasNoTitle))
	)
#iterate over all the rows in the file, profile for each class - reuse the code.
# end up with category --> countProfiler; augment countProfiler to keep track of the *number* of total samples.

#invert keys so it is is: category --> profilerName --> countMap
#build a map of profilerName --> (set of features). Needed for laplace smoothing.

#iterate over each category
	#iterate over each profilerName
		#normalise countMap using size of (set of features) and laplace smoothing.


#pass to something that has:
#category --> keyType --> reuse countProfiler again - has the normalise values, but provide a function that allows *normalising with a Laplace smoothing term* <-- add that function to the count profiler. Hmm...so for features that don't appear in a particular class it may be necessary to supply the total number of features as an external value...hmm...and also the alpha for the laplace smoothing.
#also get the priors by going over all categories, or use provided/uniform priors...

#to classify:
#supply counts (another func: supply generator, counts up the features...(with a count profiler? nah too specific; assumes seq --> generator))
#for each class/"category":
	#looks up the features (there should be no unseen features...the point of laplace smoothing)
	#employs multinomial distribution to get probability. Multiple by prior.
	#keep track of max...
	#classify!
#another function that accepts a generator of "TrainingData" entries and keeps track of the correctly classified ones. May need to move "TrainingData" class out of enhancer-specific code into this more general thing.

class NaiveBayesClassifier(object):
	def __init__(self,conditionalProbGenerator,prior):
		self.prior = prior;
		self.conditionalProbGenerator = conditionalProbGenerator;
	def getClass(self,thingToClassify):
		maxProb = None;
		maxProbClass = None;
		for aClass in self.prior:
			conditionalProb = conditionalProbGenerator.getProbability(aClass,thingToClassify);
			if (maxProb == None or maxProb < conditionalProb):
				maxProb = self.prior[aClass]*conditionalProb;
				maxProbClass = aClass;
		return maxProbClass;

class MultinomialConditionalProbGenerator(object):
	def __init__(self,classToKeyToProbabilities):
		self.classToKeyToProbabilities = classToKetToProbabilities;
	def getProbability(aClass,thingToClassify):
		#assume that thingToClassify is a series of counts for key values.
		totalKeys = 0;
		successesArr = []; #to be passed in
        pSuccessesArr = [];
        for aKey in thingToClassify:
			totalKeys += thingToClassify[aKey];
            successesArr.append(thingToClassify[aKey]);
            pSuccessesArr.append(classToKeyToProbabilities[aClass][aKey]);
        return stats.multinomialProbability(successesArr, pSuccessesArr); 





