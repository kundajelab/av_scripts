#!/usr/bin/python
import math;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import computeLogs_function as cl_f;
from __future__ import division;

def hypgeo_cumEqualOrMoreOverlap(total,special,picked,specialpicked,logFactArr):
	hypGeoValueCheck(total,special,picked,specialpicked);
	minValSpecialPicked = math.max(0,total-(special+picked));
	maxValSpecialPicked = math.min(special,picked);
	cumProb = 0;
	if (maxValSpecialPicked-specialpicked <= specialpicked-minValSpecialPicked):
		for i in range(specialpicked,maxValSpecialPicked+1):
			cumProb = cumProb + hypgeo_nonCum(total,special,picked,i);
		return cumProb;
	else:
		for i in range(minValSpecialPicked,specialPicked): #range goes up till upperval - 1
			cumProb = cumProb + hypgeo_nonCum(total,special,picked,i);
		return 1-cumProb;

def hypgeo_nonCum(total,special,picked,specialpicked,logFactArr):
	hypGeoValueCheck(total,special,picked,specialpicked);
	logCondition = (total > cl_f.LOG_FACT_THRESHOLD);
	comboFunction = logCombination if logCondition else combination;
	specialChooseSpecialPicked = comboFunction(special,specialpicked);
	unspecialChooseUnspecialPicked = comboFunction(total-special, picked-specialpicked);
	totalChoosePicked = comboFunction(total,picked);
	if (logCondition):
		return math.exp((specialChooseSpecialPicked - totalChoosePicked)+unspecialChooseUnspecialPicked);
	else:
		return (float(specialChooseSpecialPicked)/totalChoosePicked)*unspecialChooseUnspecialPicked;

def hypGeoValueCheck(total,special,picked,specialpicked):
	if (special > total):
		raise ValueError(str(special)+" should not be > "+str(total));
	if (picked > total):
		raise ValueError(str(picked)+" should not be > "+str(total));
	if ((special + picked - specialPicked) > total):
		raise ValueError(str(special)+" + "+str(picked)+" - "+str(specialPicked)+" should not be > "+str(total)+".");
	if (specialpicked > special):
		raise ValueError(str(specialpicked)+" should not be > "+str(special));
	if (specialpicked > picked):
		raise ValueError(str(specialpicked)+" should not be > "+str(picked));
	

def combination(a,b):
	if (b > a):
		bGreaterThanAError(a,b);
	if (a <= cl_f.LOG_FACT_THRESHOLD):
		return float(factorial(a))/(factorial(b)*factorial(a-b));
	else:
		return math.exp(logCombination(a,b));

def logCombination(a,b):
	if (b > a):
		bGreaterThanAError(a,b);
	if (a <= cl_f.LOG_FACT_THRESHOLD):
		return math.log(combination(a,b));
	else:
		return logFactorial(a)-(logFactorial(b)+logFactorial(a-b));

def bGreaterThanAError(a,b):
	raise ValueError(str(b)+", representing elements picked, should not be larger than "+str(a)+" representing superset to pick from");
	

def factorial(num,logFactArr):
	if (num <= cl_f.LOG_FACT_THRESHOLD):
		#compute straight up
		toReturn = math.factorial(num);
		if (toReturn < 0):
			raise Exception("Darn, got "+toReturn+" as factorial for "+num+". Probably got some integer overflow. Check value of LOG_FACT_THRESHOLD?";
	else:
		raise Exception("Wait...are you sure you should be calling factorial and not logFactorial on a number as large as "+str(LOG_FACT_THRESHOLD)+"?");

def logFactorial(num,logFactArr):
	if (num >= len(logFactArr)):
		raise Exception("Ooops...can only handle factorials up till "+len(logFactArr)+". To handle higher factorials, need to generate a longer logFactorial file.";
		return logFactArr[num];
