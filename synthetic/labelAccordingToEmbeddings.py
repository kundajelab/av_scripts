#!/usr/bin/env python
#contains classes useful for when you are labelling
#sequences according to the contents of their embeddings
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
from synthetic import synthetic as sn;

class LabelFromEmbeddings(object):
    def __init__(self, labelName):
        self.labelName = labelName;
    def isPositive(self, embeddings):
        raise NotImplementedError(); 

class LabelIfRuleSatisfied(LabelFromEmbeddings):
    """
        Label if a particular rule is satisfied
    """ 
    def __init__(self, labelName, rule):
        super(LabelIfRuleSatisfied, self).__init__(labelName);
        self.rule = rule;
    def isPositive(self, embeddings):
        return self.rule(embeddings);

class FixedLabelFromEmbeddings(LabelFromEmbeddings):
    """
        Label always present
    """ 
    def isPositive(self, embeddings):
        return True; 

