from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to the av_scripts repo");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;

#convenience class to keep track of the balance of
#positive/negative examples for each label
class LabelRepresentationCounter(object):
    def __init__(self):
        self.posExamples = 0;
        self.negExamples = 0;
    def update(self, val):
        assert val == 0 or val == 1;
        if (val == 0):
            self.negExamples += 1;
        if (val == 1):
            self.posExamples += 1;
    def merge(self,otherCounter):
        toReturn = LabelRepresentationCounter();
        toReturn.posExamples = self.posExamples + otherCounter.posExamples;
        toReturn.negExamples = self.negExamples + otherCounter.negExamples;
        return toReturn;
    def finalise(self): #TODO: normalise so that the weight is even across tissue labels
        self.positiveWeight = 0 if self.posExamples == 0 else float(self.posExamples + self.negExamples)/(self.posExamples);
        self.negativeWeight = 0 if self.negExamples == 0 else float(self.posExamples + self.negExamples)/(self.negExamples);

