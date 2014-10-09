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


#import the countProfiler function.
#iterate over all the rows in the file, profile for each class - reuse the code.
# end up with category --> countProfiler; augment countProfiler to keep track of the *number* of total samples.

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
