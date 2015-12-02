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
from collections import OrderedDict
import random;

class Manager(object):
    def __init__(self):
        self.generatorNameToGenerator = OrderedDict();
    def prepareNextSet(self):
        for generator in self.generatorNameToGenerator.values():
            generator.prepareNextSet(); 
    def getValForThisSet(self, valGeneratorName):
        return self.generatorNameToGenerator[valGeneratorName].getValForThisSet(self);
    def registerGenerator(self, name, generator):
        if name in self.generatorNameToGenerator:
            raise RuntimeError("Generator with name "+str(name)+" has already been registered");
        self.generatorNameToGenerator[name] = generator;
    def getTrackedValGenNames(self):
        """
            Returns the names of all val generators that are designated
                as tracked (val generators are tracked by default)
        """
        trackedValGenNames = [];
        for (valGeneratorName, valGenerator) in self.generatorNameToGenerator.items():
            if valGenerator.isTracked:
                trackedValGenNames.append(valGeneratorName); 
        return trackedValGenNames;
    def getGeneratedValsForThisSet(self):
        """
            All the values from valGenerators that had a genered value. If
                the valGenerator was never called for the set, it's left out.
        """
        activeGeneratorsForThisSet = OrderedDict();
        for (valGeneratorName, valGenerator) in self.generatorNameToGenerator.items():
            if (valGenerator.wasValGeneratedForSet):
                activeGeneratorsForThisSet[valGeneratorName] = valGenerator.getValForThisSet(self); 
        return activeGeneratorsForThisSet;

class AbstractValGenerator(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self, isTracked=True):
        self._isTracked = isTracked;
        self._wasValGeneratedForSet = False;
    def prepareNextSet(self):
        #val for this set stores the cached value
        self.valForThisSet = None;     
        self._wasValGeneratedForSet = False;
    @abc.abstractmethod
    def generate(self, manager):
        raise NotImplementedError();
    def getValForThisSet(self, manager):
        if hasattr(self, "valForThisSet")==False:
            raise RuntimeError("Hmm...did you call prepareNextSet first?");
        if self.valForThisSet is None:
            self.valForThisSet = self.generate(manager);
            self._wasValGeneratedForSet = True;
        return self.valForThisSet;           
    @property
    def isTracked(self):
        return self._isTracked;
    @property
    def wasValGeneratedForSet(self):
        return self._wasValGeneratedForSet;

class SampleFromDiscreteDistribution(AbstractValGenerator):
    def __init__(self, discreteDistribution, **kwargs):
        """
            discreteDistribution: instance of util.DiscreteDistribution
        """
        super(SampleFromDiscreteDistribution, self).__init__(**kwargs);
        self.discreteDistribution = discreteDistribution; 
    def generate(self, manager):
        return util.sampleFromDiscreteDistribution(self.discreteDistribution); 

class CustomGenerator(AbstractValGenerator):
    def __init__(self, generatorFunc, **kwargs):
        super(CustomGenerator, self).__init__(**kwargs);
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
        return cast(util.sampleFromRangeWithStepSize(minVal=minVal, maxVal=maxVal, stepSize=step, cast=float));
    return generatorFunc;

class RandArray(AbstractValGenerator):
    """
        randomly sample from an array
    """
    def __init__(self, array, **kwargs):
        super(RandArray, self).__init__(**kwargs);
        assert array is not None;
        self.array = array;
    def generate(self, manager):
        return self.array[int(random.random()*len(self.array))];

class RandRange(AbstractValGenerator):
    def __init__(self, minVal, maxVal, step=1, cast=float, **kwargs):
        super(RandRange, self).__init__(**kwargs);
        self.minVal = minVal;
        self.maxVal = maxVal;
        self.step = step;
        self.cast=cast;
    def generate(self, manager):
        return self.cast(util.sampleFromRangeWithStepSize(minVal=self.minVal, maxVal=self.maxVal, stepSize=self.step, cast=float)); 

class ArrWrap(AbstractValGenerator):
    def __init__(self, *generators, **kwargs):
        super(ArrWrap, self).__init__(**kwargs);
        self.generators = generators;
    def prepareNextSet(self):
        super(ArrWrap, self).prepareNextSet();
        for generator in self.generators:
            generator.prepareNextSet(); 
    def generate(self, manager):
        return [x.getValForThisSet(manager) for x in self.generators]; 

