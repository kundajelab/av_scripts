#!/usr/bin/env python
from __future__ import absolute_import;
from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import argparse;
from pwm import scoreSeq;
from pwm import pwm;
from itertools import izip;
import numpy as np;
from sklearn.cross_validation import train_test_split;
from sklearn.tree import DecisionTreeClassifier;
from sklearn.grid_search import GridSearchCV;
from sklearn.metrics import accuracy_score;
from sklearn.metrics import confusion_matrix;

CLASSIFIER_TYPE = util.enum(decisionTree="decisionTree");
SCORING = util.enum(roc_auc='roc_auc', accuracy='accuracy', recall='recall');

def runDecisionTree(scoringResultList, scoringResultListTrainValid, scoringResultListTest, labelsTrainValid, labelsTest, options):
	# Run a decision tree classifier on the top PWMs
	if (len(labelsTrainValid == 0) == 0) or (len(labelsTrainValid == 1) == 0):
		# There are no examples in the training/validation set from one of the classes
		raise RuntimeError("Only one class is present in the training/validation set")
	ind_0 = labelsTest == 0
	ind_1 = labelsTest == 1
	if (len(ind_0) == 0) or (len(ind_1) == 0):
		# There are no examples in the test set from one of the classes
		raise RuntimeError("Only one class is present in the test set")
	tuned_parameters = [{'max_depth': range(1, options.topN + 1), 'max_features': [options.topN]}]
	clf = GridSearchCV(DecisionTreeClassifier(), tuned_parameters, cv=5, n_jobs=4, scoring=str(options.scoring))
	clf.fit(scoringResultListTrainValid, labelsTrainValid)
	labelsPred = clf.predict(scoringResultListTest)
	acc = accuracy_score(labelsTest, labelsPred)
	sensitivity = accuracy_score(labelsTest[ind_1], labelsPred[ind_1])
	specificity = accuracy_score(labelsTest[ind_0], labelsPred[ind_0])
	if options.verbose:
		# Print information from the classifier
		print("Best parameters set found:")
		print(clf.best_params_)
		print("Grid scores:")
		for params, meanScore, scores in clf.grid_scores_:
			# Iterate through the information from the decision tree and print all of it
			print("%0.3f (+/-%0.03f) for %r" % (meanScore, scores.std() * 2, params))
		print ("Test accuracy:")
		print(acc)
		print ('Test Confusion Matrix:')
		print(confusion_matrix(labelsTest, labelsPred))
		print ("Sensitivity: " + str(sensitivity))
		print ("Specificity: " + str(specificity))
	preds = clf.predict(scoringResultList)
	return [acc, sensitivity, specificity, preds]

def runClassifier(scoringResultList, scoringResultListTrainValid, scoringResultListTest, labelsTrainValid, labelsTest, options):
	# Run the classifier
	if options.classifierType == CLASSIFIER_TYPE.decisionTree:
		# Run a decision tree classifier
		[acc, sensitivity, specificity, preds] = runDecisionTree(scoringResultList, scoringResultListTrainValid, scoringResultListTest, labelsTrainValid, labelsTest, options)
	else:
		raise RuntimeError("Unsupported classifier "+str(options.classifierType))
	return [acc, sensitivity, specificity, preds]

def getPWMPerformance(options):
	# Use a regression tree to get the performance from the pwm
	scoringResultList = scoreSeq.scoreSeqs(options)
	labels = np.loadtxt(options.labelsFile, dtype="int", skiprows=1)
	[scoringResultListTrainValid, scoringResultListTest, labelsTrainValid, labelsTest] = train_test_split(scoringResultList, labels, test_size=options.testFrac)
	[acc, sensitivity, specificity, preds] = runClassifier(scoringResultList, scoringResultListTrainValid, scoringResultListTest, labelsTrainValid, labelsTest, options)
	of = open(options.outputFile, 'w+')
	of.write("Test accuracy" + "\t" + str(acc) + "\n")
	of.write("Sensitivity" + "\t" + str(sensitivity) + "\n")
	of.write("Specificity" + "\t" + str(specificity) + "\n")
	for (l, p) in izip(labels, preds):
		# Iterate through the labels and predictions and output both
		of.write(str(l) + "\t" + str(p) + "\n")
	of.close()
	
if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--motifsFile", required=True);
    parser.add_argument("--pwmName", required=True); 
    parser.add_argument("--pseudocountProb", type=float, default=0.001); 
    parser.add_argument("--fileToScore", required=True); # This is assumed to have a header
    parser.add_argument("--seqCol", type=int, default=1); # This is 0-indexed
    parser.add_argument("--auxillaryCols", type=int, nargs="+", default=[0,1]);
    parser.add_argument("--scoreSeqMode", choices=pwm.SCORE_SEQ_MODE.vals, default="topN");
    parser.add_argument("--topN", type=int, required=True);
    parser.add_argument("--greedyTopN", action="store_true");
    parser.add_argument("--reverseComplementToo", action="store_true");
    parser.add_argument("--labelsFile", required=True); # This is assumed to have a header; line i corresponds to line i in fileToScore
    parser.add_argument("--outputFile", required=True);
    parser.add_argument("--classifierType", choices=CLASSIFIER_TYPE.vals, default="decisionTree")
    parser.add_argument("--scoring", choices=SCORING.vals, default='roc_auc')
    parser.add_argument("--testFrac", type=float, default=0.3)
    parser.add_argument("--verbose", action="store_true");
    options = parser.parse_args();
    if (options.greedyTopN):
        if (options.topN is None):
            raise RuntimeError("topN should not be none if greedyTopN flag is specified");
    getPWMPerformance(options);