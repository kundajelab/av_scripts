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
        return self.generatorNameToGenerator[valGeneratorName].getValForThisSet();
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
    def generate(self):
        raise NotImplementedError();
    def getValForThisSet(self):
        if hasattr(self, "valForThisSet")==False:
            raise RuntimeError("Hmm...did you call prepareNextSet first?");
        if self.valForThisSet is None:
            self.valForThisSet = self.generate();
        return self.valForThisSet;           

class CustomGenerator(AbstractValGenerator):
    def __init__(self, generatorFunc):
        self.generatorFunc=generatorFunc;
    def generate(self):
        return self.generatorFunc(manager);

def getDynamicRangeGeneratorFunc(valGeneratorName, minFunc, maxFunc, stepFunc):
    def generatorFunc(manager):
        val = manager.getValForThisSet(valGeneratorName); 
        minVal = minFunc(val);
        maxVal = maxFunc(val);
        step = stepFunc(val); 
        return util.sampleFromRangeWithStride(minVal, maxVal, step);
    return generatorFunc;

class RandArray(AbstractValGenerator):
    """
        randomly sample from an array
    """
    def __init__(self, array):
        self.array = array;
    def generate(self):
        return self.array[int(random.random()*len(self.array)];

class RandRange(AbstractValGenerator):
    def __init__(self, minVal, maxVal, step=1):
        self.minVal = minVal;
        self.maxVal = maxVal;
        self.step = step;
    def generate(self):
        return util.sampleFromRangeWithStride(self.minVal, self.maxVal, self.step); 

class ArrWrap(AbstractValGenerator):
    def __init__(self, *generators):
        self.generators = generators;
    def generate(self):
        return [x.generate() for x in self.generators]; 

def createValGeneratorManager(options):
    """
        options.resolution: resolution for things like stride and width
        options.seedsToTry
        options.minMaxpoolWidth
        options.maxMaxpoolWidth
        options.strideLowerBoundFold: stride lower bound will be width/this,
                                        rounded to nearest resolution
        options.minFcSize, options.maxFcSize
        options.optimizersToTry - should limit to those that don't
            need substantial hyperparam tuning
        options.minConvNumFilters, options.maxConvNumFilters
        options.minConvKernelWidth, options.maxConvKernelWidth
    """
    valGenNames=util.enum(seed='seed', convLayers_numFilters='convLayers_numFilters'
                            ,convLayers_kernelWidths='convLayers_kernelWidths'
                            ,maxPool_width='maxPool_width'
                            ,maxPool_stride_width='maxPool_stride_width'
                            ,fcLayer_sizes='fcLayer_sizes'
                            ,optimizerType='optimizerType'
                            ,batchSize='batchSize')
    manager = Manager();
    manager.registerGenerator(name=valGenNames.seed, generator=RandArray(options.seedsToTry));
    manager.registerGenerator(name=valGenNames.maxPool_width, generator=RandRange(options.minMaxpoolWidth,options.maxMaxpoolWidth,step=options.resolution))
    manager.registerGenerator(name=valGenNames.maxPool_stride, generator=CustomGenerator(generatorFunc=valGen.getDynamicRangeGenerator(
                                                                    valGeneratorName=valGenNames.maxPool_width
                                                                    ,minFunc=lambda x: min(util.roundToNearest(float(x)/options.strideLowerBoundFold, options.resolution), x)
                                                                    ,maxFunc=lambda x: x
                                                                    ,stepFunc=lambda x: options.resolution
                                                                ));
    manager.registerGenerator(name=valGenNames.fcLayers_sizes, generator=ArrWrap(RandRange(options.minFcSize, options.maxFcSize)))
    manager.registerGenerator(name=valGenNames.optimizerType, generator=RandArray(options.optimizersToTry));
    manager.registerGenerator(name=valGenNames.convLayers_numFilters, generator=ArrWrap(RandRange(options.minConvNumFilters, options.maxConvNumFilters,1)))
    manager.registerGenerator(name=valGenNames.convLayers_kernelWidths, generator=ArrWrap(RandRange(options.minConvKernelWidth, options.maxConvKernelWidth,1)))
    manager.registerGenerator(name=valGenNames.batchSize, generator=RandRange(options.minBatchSize, options.maxBatchSize, options.batchSizeInterval))
    return manager;
