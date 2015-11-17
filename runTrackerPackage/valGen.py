#!/usr/bin/env python
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
import abc;
from collections import namedtuple
import random;

class Manager(object):
    def __init__(self):
        self.generatorNameToGenerator = {};
    def prepareNextSet(self):
        for generator in self.generatorNameToGenerator.values():
            generator.prepareNextSet(); 
    def getValForThisSet(self, valGeneratorName):
        return self.generatorNameToGenerator[valGeneratorName].getValForThisSet(self);
    def registerGenerator(self, name, generator):
        if name in self.generatorNameToGenerator:
            raise RuntimeError("Generator with name "+str(name)+" has already been registered");
        self.generatorNameToGenerator[name] = generator;

class AbstractValGenerator(object):
    __metaclass__ = abc.ABCMeta
    def prepareNextSet(self):
        #val for this set stores the cached value
        self.valForThisSet = None;     
    @abc.abstractmethod
    def generate(self, manager):
        raise NotImplementedError();
    def getValForThisSet(self, manager):
        if hasattr(self, "valForThisSet")==False:
            raise RuntimeError("Hmm...did you call prepareNextSet first?");
        if self.valForThisSet is None:
            self.valForThisSet = self.generate(manager);
        return self.valForThisSet;           

class SampleFromDiscreteDistribution(AbstractValGenerator):
    def __init__(self, discreteDistribution):
        """
            discreteDistribution: instance of util.DiscreteDistribution
        """
        self.discreteDistribution = discreteDistribution; 
    def generate(self, manager):
        return util.sampleFromDiscreteDistribution(self.discreteDistribution); 

class CustomGenerator(AbstractValGenerator):
    def __init__(self, generatorFunc):
        self.generatorFunc=generatorFunc;
    def generate(self, manager):
        return self.generatorFunc(manager);

def getDynamicRangeGeneratorFunc(valGeneratorName, minFunc, maxFunc, stepFunc, cast=float):
    def generatorFunc(manager):
        val = manager.getValForThisSet(valGeneratorName); 
        minVal = minFunc(val);
        maxVal = maxFunc(val);
        step = stepFunc(val); 
        assert minVal > 0;
        return cast(util.sampleFromRangeWithStride(minVal, maxVal, step));
    return generatorFunc;

class RandArray(AbstractValGenerator):
    """
        randomly sample from an array
    """
    def __init__(self, array):
        assert array is not None;
        self.array = array;
    def generate(self, manager):
        return self.array[int(random.random()*len(self.array))];

class RandRange(AbstractValGenerator):
    def __init__(self, minVal, maxVal, step=1, cast=float):
        self.minVal = minVal;
        self.maxVal = maxVal;
        self.step = step;
        self.cast=cast;
    def generate(self, manager):
        return self.cast(util.sampleFromRangeWithStride(self.minVal, self.maxVal, self.step)); 

class ArrWrap(AbstractValGenerator):
    def __init__(self, *generators):
        self.generators = generators;
    def prepareNextSet(self):
        super(ArrWrap, self).prepareNextSet();
        for generator in self.generators:
            generator.prepareNextSet(); 
    def generate(self, manager):
        return [x.getValForThisSet(manager) for x in self.generators]; 

