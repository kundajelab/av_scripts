#!/usr/bin/python
import math;
from scipy.stats import norm;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import computeLogs_function as cl_f;

class TestResult:
	def __init__(self,pval,testType,testStatistic=None,testContext=None):
		self.pval = pval;
		self.testType = testType;
		self.testStatistic=testStatistic;
		self.testContext=testContext;
	def __str__(self):
		toReturn = "pval: "+str(self.pval)+", test: "+self.testType;
		if (self.testStatistic is not None):
			toReturn += ", test statistic: "+str(self.testStatistic);
		if (self.testContext is not None):
			toReturn += ", test context: "+str(self.testContext);
		return toReturn;

#flips between Z-test and fisher's exact test based on supplied data
def proportionTest(total,special,picked,specialPicked):
	if (total <= cl_f.LOG_FACTORIAL_THRESHOLD):
		method=hypGeo_cumEqualOrMoreOverlap;
	elif ((specialPicked > 5) and (picked-specialPicked > 5) and (special-specialPicked > 5) and (total-special+specialPicked > 5)):
		method=twoProportionZtest;
	else:
		method=edgeCase
	return method(total,special,picked,specialPicked);

def edgeCase(total,special,picked,specialPicked):
	hypGeoValueCheck(total,special,picked,specialPicked);
	if (picked == total and specialPicked == special):
		return TestResult(1.0,"Common sense");
	if (specialPicked == 0):
		return TestResult(1.0,"Common sense");
	return hypGeo_cumEqualOrMoreOverlap(total,special,picked,specialPicked,bruteCompute=True);
	#if (picked < cl_f.LOG_FACTORIAL_THRESHOLD):
	#	#do a desperate binomial estimate
	#	return binomialProbability(specialPicked,picked,float(special)/total);
	#raise Exception("No supported test for edge case where "
	#	+"total="+str(total)+", special="+str(special)
	#	+", picked="+str(picked)+" and specialPicked="+str(specialPicked));

def binomialProbability(trials,successes,pSuccess):
	combos = combination(trials,successes);
	return TestResult(combos*(pSuccess**(successes)), "binomial probability");

#for when fisher's exact test doesn't scale
def twoProportionZtest(total,special,picked,specialPicked):
	hypGeoValueCheck(total,special,picked,specialPicked);
	enOne = float(picked);
	enTwo = float(total-picked);
	pOne = float(specialPicked)/enOne;
	pTwo = float(special-specialPicked)/enTwo;
	pMean = float(special)/total;
	z = float(pOne-pTwo)/((pMean*(1-pMean)*(1/enOne + 1/enTwo))**(0.5))
	
	return TestResult(1-norm.cdf(z),"Two-proportion z-test", testStatistic=z);

def hypGeo_cumEqualOrMoreOverlap(total,special,picked,specialPicked,bruteCompute=False):
	hypGeoValueCheck(total,special,picked,specialPicked);
	minValSpecialPicked = max(0,(special+picked)-total);
	maxValSpecialPicked = min(special,picked);
	cumProb = 0;
	if (maxValSpecialPicked-specialPicked <= specialPicked-minValSpecialPicked):
		for i in range(specialPicked,maxValSpecialPicked+1):
			cumProb = cumProb + hypGeo_nonCum(total,special,picked,i,bruteCompute);
		toReturn = cumProb;
	else:
		for i in range(minValSpecialPicked,specialPicked): #range goes up till upperval - 1
			cumProb = cumProb + hypGeo_nonCum(total,special,picked,i,bruteCompute);
		toReturn = 1-cumProb;
	return TestResult(toReturn, "hypergeometric test");

def hypGeo_nonCum(total,special,picked,specialPicked,bruteCompute=False):
	hypGeoValueCheck(total,special,picked,specialPicked);
	logCondition = (total > cl_f.LOG_FACTORIAL_THRESHOLD);
	comboFunction = logCombination if logCondition else combination;
	specialChooseSpecialPicked = comboFunction(special,specialPicked,bruteCompute);
	unspecialChooseUnspecialPicked = comboFunction(total-special, picked-specialPicked,bruteCompute);
	totalChoosePicked = comboFunction(total,picked,bruteCompute);
	if (logCondition):
		return math.exp((specialChooseSpecialPicked - totalChoosePicked)+unspecialChooseUnspecialPicked);
	else:
		return (float(specialChooseSpecialPicked)/totalChoosePicked)*unspecialChooseUnspecialPicked;

def hypGeoValueCheck(total,special,picked,specialPicked):
	if (special > total):
		raise ValueError(str(special)+" should not be > "+str(total));
	if (picked > total):
		raise ValueError(str(picked)+" should not be > "+str(total));
	if ((special + picked - specialPicked) > total):
		raise ValueError(str(special)+" + "+str(picked)+" - "+str(specialPicked)+" should not be > "+str(total)+".");
	if (specialPicked > special):
		raise ValueError(str(specialPicked)+" should not be > "+str(special));
	if (specialPicked > picked):
		raise ValueError(str(specialPicked)+" should not be > "+str(picked));
	

def combination(a,b,bruteCompute=False):
	if (b > a):
		bGreaterThanAError(a,b);
	if (a <= cl_f.LOG_FACTORIAL_THRESHOLD):
		return factorial(a)/(factorial(b)*factorial(a-b)); #shouldn't need floats cos integers should divide exactly!
	else:
		return math.exp(logCombination(a,b,bruteCompute));

def logCombination(a,b,bruteCompute=False):
	if (b > a):
		bGreaterThanAError(a,b);
	if (a <= cl_f.LOG_FACTORIAL_THRESHOLD):
		return math.log(combination(a,b));
	else:
		return logFactorial(a,bruteCompute=bruteCompute)-(logFactorial(b,bruteCompute=bruteCompute)+logFactorial(a-b,bruteCompute=bruteCompute));

def bGreaterThanAError(a,b):
	raise ValueError(str(b)+", representing elements picked, should not be larger than "+str(a)+" representing superset to pick from");
	

def factorial(num):
	if (num <= cl_f.LOG_FACTORIAL_THRESHOLD):
		#compute straight up
		toReturn = math.factorial(num);
		if (toReturn < 0):
			raise Exception("Darn, got "+toReturn+" as factorial for "+num+". Probably got some integer overflow. Check value of LOG_FACTORIAL_THRESHOLD?");
	else:
		raise Exception("Wait...are you sure you should be calling factorial and not logFactorial on a number as large as "+str(LOG_FACTORIAL_THRESHOLD)+"?");
	return toReturn

def logFactorial(num,logFactArr=cl_f.LOG_FACTORIAL_ARRAY,bruteCompute=False):
	if (num >= len(logFactArr)):
		if (bruteCompute==False):
			raise Exception("Ooops...can only handle factorials up till "+str(len(logFactArr))+". To handle higher factorials like "+str(num)+", need to generate a longer logFactorial file or set bruteCompute to true");
		else:
			print "Warning: brute computing logFactorial of "+str(num)+".";
			return cl_f.computeLogFactorial(num);	
	return logFactArr[num];
