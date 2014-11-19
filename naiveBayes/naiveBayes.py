#!/usr/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import math;
import fileProcessing as fp;

def trainNaiveBayes(options):
    trainingFile = fp.getFileHandle(options.trainingFile);
    naiveBayesLearner = NaiveBayesLearner();
    def action(inp,lineNumber): #to be performed on each line of the training file
        if (lineNumber%options.progressUpdate == 0):
            print "Processed "+str(lineNumber)+" lines of training file";
        sequence = inp[options.sequenceColIndex].upper();
        category = inp[options.categoryColIndex];
        naiveBayesLearner.processInput(category,sequence);
    fp.performActionOnEachLineOfFile(trainingFile, action=action, ignoreInputTitle=True, transformation=util.chainFunctions(fp.trimNewline, fp.splitByTabs)); 
    
    naiveBayesClassifier = naiveBayesLearner.laplaceSmoothAndReturn();
    testingFile = fp.getFileHandle(options.testingFile);
    secondaryCategoryToCorrectClassifications = {};
    secondaryCategoryToTotalOccurences = {};
    def action(inp, lineNumber): #to be performed on each line of the testing file
        if (lineNumber%options.progressUpdate == 0):
            print "Processed "+str(lineNumber)+" lines of testing file";
        sequence = inp[options.sequenceColIndex].upper();
        category = inp[options.categoryColIndex];
        secondaryCategory = inp[options.secondaryCategoryColIndex];
        if secondaryCategory not in secondaryCategoryToTotalOccurences:
            secondaryCategoryToTotalOccurences[secondaryCategory] = 0;
            secondaryCategoryToCorrectClassifications[secondaryCategory] = 0;
        secondaryCategoryToTotalOccurences[secondarCategory] += 1;
        predictedCategory = naiveBayesClassifier.classify(sequence);
        if predictedCategory == category:
            secondaryCategoryToCorrectClassifications[secondaryCategory] += 1;
    fp.performActionOnEachLineOfFile(testingFile, action=action, ignoreInputTitle=True, transformation=util.chainFunctions(fp.trimNewline, fp.splitByTabs));
    misclassificationRates = [];
    for secondaryCategory in secondaryCategoryToCorrectClassifications:
        correct = secondaryCategoryToCorrectClassifications[secondaryCategory];
        total = secondaryCategoryToTotalOccurences[secondaryCategory];
        misclassificationRates.append({'secondaryCategory': secondaryCategory
            , 'correct': correct
            , 'total': total
            , 'misclassification': (1-float(correct)/total)});
    misclassificationRates = sorted(misclassificationRates, key=lambda x: -1*x['misclassification']);
    toPrint = [x['secondaryCategory']+": "+str(x['misclassification'])+" ("+str(x['correct'])+"/"+str(x['total'])+")" for x in misclassificationRates];
    print "\n".join(toPrint);

class NaiveBayesLearner(object):
    def __init__(self):
        self.categoryToFeatureToCounts = {};
        self.categoryToTotalFeaturesSeen = {};
        self.categoryToCategoryOccurences = {};
        self.totalExamplesSeen = 0;
        self.allFeaturesSeen = {}; #really a set, I'm using a dictionary cos I'm lazy about looking up syntax
   
    def processInput(category, featureGenerator):
        self.totalExamplesSeen += 1;
        if category not in self.categoryToCategoryOccurences:
            self.categoryToCategoryOccurences[category] = 0;
            self.categoryToFeatureToCounts[category] = {};
            self.categoryToTotalFeaturesSeen[category] = 0;
        for feature in featureGenerator:
            if feature not in self.categoryToFeatureToCounts[category]:
                self.categoryToFeatureToCounts[category][feature] = 0;
            self.categoryToFeatureToCounts[category][feature] += 1;
            self.categoryToTotalFeaturesSeen[category] += 1;
 
    def laplaceSmoothAndReturn(self):
        numFeatures = len(keys(self.allFeaturesSeen));
        categoryToFeatureToProbability = {};
        categoryToPriorProbability = {};
        for category in categoryToFeatureCounts:
            categoryToPriorProbability = float(self.categoryToCategoryOccurences[category])/self.totalExamplesSeen;
            categoryToFeatureToProbability[category] = {};
            denominator = self.categoryToTotalFeaturesSeen[category] + numFeatures;
            for feature in self.allFeaturesSeen:
                #initialise with laplace smoothed value
                categoryToFeatureToProbability[category][feature] = float(1)/(denominator);
            for feature in self.categoryToFeatureToCounts:
                #for the features we saw in the training set, compute the laplace smoothed prob:
                numerator = self.categoryToFeatureToCounts[category][feature] + 1;
                categoryToFeatureToProbability[category][feature] = float(numerator)/denominator;
        return NaiveBayesClassifier(categoryToPriorProbability, categoryToFeatureProbability);

class NaiveBayesClassifier(object):
    def __init__(self, categoryToPriorProbability, categoryToFeatureToProbability):
        self.categoryToPriorProbability = categoryToPriorProbability;
        self.categoryToFeatureToProbability = categoryToFeatureToProbability;   
    def classify(featureGenerator):
        categoryToLogProb = {};
        for feature in featureGenerator:
            for category in categoryToPriorProbability:
                if category not in categoryToLogProb:
                    categoryToLogProb = math.log(categoryToPriorProbability);
                if feature in categoryToFeatureToProbability[category]:
                    categoryToLogProb += math.log(categoryToFeatureToProbability[category][feature]);
                else:
                    print "Feature "+str(feature)+" did not occur in training set but appears in testing. Ignoring.";
        #find the max
        maxCategory = None;
        maxLogProb = None;
        for category in categoryToLogProb:
            if maxCategory == None or maxLogProb < categoryToLogProb[category]:
                maxCategory = category;
                maxLogProb= categoryToLogProb[category];
        return maxCategory;        


if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--trainingFile",help="Assumes a title is present", required=True);
    parser.add_argument("--testingFile",help="Assumes a title is present", required=True);
    parser.add_argument("--sequenceColIndex", type=int, default=3);
    parser.add_argument("--categoryColIndex", help="This is the class prediction is attempted for", type=int, default=2);
    parser.add_argument("--secondCategoryColIndex", help="This is used in testing stage if you want to partition the error rates by particular categories", type=int, default=1);
    parser.add_argument("--progressUpdate", type=int, default=10000);
    trainNaiveBayes(parser.parse_args());
