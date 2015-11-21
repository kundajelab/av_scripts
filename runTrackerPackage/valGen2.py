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
from util import ArgParseArgument;

class Manager(object):
    def __init__(self):
        self.generatorNameToGenerator = {};
    def prepareNextSet(self):
        for generator in self.generatorNameToGenerator.values():
            generator.prepareNextSet(); 
    def getValForThisSet(self, valGenName):
        return self.generatorNameToGenerator[valGenName].getValForThisSet(self);
    def registerGenerator(self, name, generator):
        if name in self.generatorNameToGenerator:
            raise RuntimeError("Generator with name "+str(name)
                                +" has already been registered");
        self.generatorNameToGenerator[name] = generator;
    def getTrackedValGenNames(self):
        """
            Returns the names of all val generators that are designated
                as tracked (val generators are tracked by default)
        """
        trackedValGenNames = [];
        for (valGenName, valGenerator) in self.generatorNameToGenerator.items():
            if valGenerator.isTracked:
                trackedValGenNames.append(valGenName); 
        return trackedValGenNames;
    def getGeneratedValsForThisSet(self):
        """
            All the values from valGenerators that had a genered value. If
                the valGenerator was never called for the set, it's left out.
        """
        activeGeneratorsForThisSet = {};
        for (valGenName, valGenerator) in self.generatorNameToGenerator.items():
            if (valGenerator.wasValGeneratedForSet):
                activeGeneratorsForThisSet[valGenName] = \
                                            valGenerator.getValForThisSet(self); 
        return activeGeneratorsForThisSet;

class AbstractValProvider(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getValForThisSet(self, manager):
        raise NotImplementedError();

class FixedVal(AbstractValProvider):
    def __init__(self, val):
        self.val = val;
    def getValForThisSet(self, manager):
        return self.val; 

class RefVal(AbstractValProvider):
    def __init__(self, valGenName, func=lambda x: x):
        self.valGenName = valGenName;
        self.func = func;
    def getValForThisSet(self, manager):
        return self.func(manager.getValForThisSet(self.valGenName)); 

class AbstractValGenerator(AbstractValProvider):
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

def getArgument_requiredIfNoDefault(parser, argName, default, **kwargs):
    util.ArgParseArgument(argumentName=argName, default=default
                        , required=(True if default else False), **kwargs);


ValGenRegistererAndName = namedtuple("ValGenRegistererAndName"
                            ,["valGenRegisterer", "name"]);

class AbstractValGenRegisterer(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.kwargsForRegister = OrderedDict();
        self.argParseKwargs = OrderedDict();
        self.hasInternalNameToArgparseArgs = False;
    def setKwargs(self, **kwargs):
        for val in kwargs.values():
            assert isinstance(val,AbstractValProvider);
        self.kwargsForRegister.update(kwargs);
        return self; 
    def setFixedKwargs(self, **kwargs):
        self.kwargsForRegister.update(
            dict([(x, FixedVal(kwargs[x])) for x in kwargs]));
        return self;
    def setArgParseKwargs(self, **kwargs):
        """
            Any values which you want to user to provide at the command
                line via an argument parser get be specified here.
            key: argument name (argument needed for _register)
            value: argparse kwargs MINUS the argument name
        """
        self.argParseKwargs.update(kwargs); 
        return self;
    def setKwargsFromRegisteredValGenerator(self, **kwargs):
        #TODO: implement
        raise NotImplementedError();
    def getArgParseArgs(self, prefix=None):
        prefix = "" if prefix is None else prefix+"_";
        self.internalNameToArgParseArgs = OrderedDict([(x,
                                util.ArgParseArgument(argumentName=prefix+x,
                                **self.argParseKwargs[x]))
                                     for x in self.argParseKwargs]);
        self.hasInternalNameToArgparseArgs = True;
        return self.internalNameToArgParseArgs.values();
    def addArgParseArgsToParser(self, parser, prefix=None):
        argParseArgs = self.getArgParseArgs(prefix=prefix);
        for arg in argParseArgs:
            arg.addToParser(parser); 
    def getArgParseObject(self, description, prefix=None):
        parser = argparse.ArgumentParser(description=description); 
        self.addArgParseOptsToParser(parser, prefix);
        return parser;
    def register(self, manager, options, valGenName):
        assert hasattr(
        finalKwargs = {};
        finalKwargs.update(self.kwargsForRegister);
        if (self.hasInternalNameToArgparseArgs):
            for internalName in self.internalNameToArgParseArgs:
                finalKwargs[internalName] = getattr(options,
                        internalNameToArgParseArgs[internalName].argumentName); 
        #todo: register the dependent val generators specified.
        self._register(manager, valGenName, **finalKwargs); 
    @abstractmethod
    def _register(self, manager, valGenName, **kwargs):
        raise NotImplementedError(); 

class BasicValGenRegisterer(AbstractValGenRegisterer):
    def __init__(self, valGenCreationFunc):
        self.valGenCreationFunc = valGenCreationFunc;
    def _register(self, manager, valGenName, **kwargs):
        valGenerator = self.valGenCreationFunc(**kwargs);
        manager.registerGenerator(name=valGenName, generator=valGenerator);




