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
        for (valGenName, valGen) in self.generatorNameToGenerator.items():
            if valGen.isTracked:
                trackedValGenNames.append(valGenName); 
        return trackedValGenNames;
    def getGeneratedValsForThisSet(self):
        """
            All the values from valGens that had a genered value. If
                the valGen was never called for the set, it's left out.
        """
        activeGeneratorsForThisSet = {};
        for (valGenName, valGen) in self.generatorNameToGenerator.items():
            if (valGen.wasValGeneratedForSet):
                activeGeneratorsForThisSet[valGenName] = \
                                            valGen.getValForThisSet(self); 
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

class ParamValProvider(AbstractValProvider):
    def __init__(self, paramName, valProvider):
        self.paramName = paramName;
        self.valProvider = valProvider;
    def getValForThisSet(self, manager):
        return "--"+self.paramName+" "+self.valProvider.getValForThisSet(manager);

class AbstractValGenerator(AbstractValProvider):
    def __init__(self, isTracked):
        self._isTracked = isTracked;
        self._wasValGeneratedForSet = False;
    def prepareNextSet(self):
        #val for this set stores the cached value
        self.valForThisSet = None;     
        self._wasValGeneratedForSet = False;
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
    @abc.abstractmethod
    def generate(self, manager):
        raise NotImplementedError();

class ValGenerator(AbstractValGenerator):
    __metaclass__ = abc.ABCMeta
    def __init__(self, generatorFunc, isTracker):
        super(ValGenerator, self).__init__(isTracked=isTracker);
        self.generatorFunc = generatorFunc;
    def generate(self, manager):
        return self.generatorFunc(manager); 


def getArgument_requiredIfNoDefault(parser, argName, default, **kwargs):
    util.ArgParseArgument(argumentName=argName, default=default
                        , required=(True if default else False), **kwargs);


ValGenRegistererAndName = namedtuple("ValGenRegistererAndName"
                            ,["valGenRegisterer", "name"]);

class IValGenRegisterer(object):
    """
        I am mimicking java with an interface declaration here,
            for simplicity of documentation.
    """
    @abc.abstractmethod
    def setValGenName(self, valGenName):
        """
            Fix the name of the val generator
                that will be registered
        """
        raise NotImplementedError();
    @abc.abstractmethod
    def addArgParseArgsToParser(self, parser):
        """
            add any arguments needed to do the registeration to an
            ArgumentParser object, which is used to create the
            options object that is passed to register(manager, options).
        """
        raise NotImplementedError();
    @abc.abstractmethod
    def register(manager, options):
        """
            will register a val generator.
            The val generator name is set via setValGenName
        """
        raise NotImplementedError();
    

class AbstractValGenRegisterer(IValGenRegisterer):
    __metaclass__ = abc.ABCMeta
    """
        Philosophy: define a function, _getValGen, which
            takes (manager, valGenName, options, **kwargs) as input,
            where **kwargs are all valProviders, and returns a ValGenerator
            to be registered with the name valGenName. The only reason
            valGenName is part of the signature is if it helps with the creation
            of things needed by the valGen. This function does not do the registering,
            but it may register dependent valGens that aren't going to be
            registered by other mechanisms.
        _getValGen takes multiple kwargs as input. The values of these
            kwargs are specified using the following functions:
            setKwargs, setFixedKwargs, setArgParseKwargs, setKwargsFromSubRegisterers.
            Those functions all return 'self' so can be chained via the builder pattern.
            Then, when register is called, _getValGen will be called and registered.
        By calling register(manager, valGenName, options),
            _getValGen will be called, in addition to the register(...) function of
            any subRegisterers provided by setKwargsFromSubRegisterers.
        The register function will call 'prepareFinalKwargs'. It compiles
            all the information that was specified via the setKwarg functions above.
            prepareFinalKwargs takes an options object, generated via argparse.
        If some kwargs were specified via setArgParseKwargs, it is necessary to call
            getArgParseArgs at some point and apply the represented arguments to an
            ArgumentParse object.
    """
    def __init__(self):
        self.kwargsAsIs = OrderedDict();
        self.kwargsFromArgParse = OrderedDict();
        self.kwargNameToArgParseName = None;
        self.kwargsFromSubRegisterer = OrderedDict();
        self.finalKwargs = None;
        self.valGenName=None;
    def setValGenName(self, valGenName):
        self.valGenName = valGenName;
    def assertValGenNameSet(self):
        if (self.valGenName is None):
            raise RuntimeError("Need to call setValGenName before you call this");
    def register(self, manager, options):
        self.assertValGenNameSet();
        self.prepareFinalKwargs(manager, self.valGenName, options);
        valGen = self._getValGen(manager, self.valGenName, options, **self.finalKwargs); 
        manager.registerGenerator(name=self.valGenName, generator=valGen);
    def updateFinalKwargs(self, kwargs):
        for kwarg in kwargs:
            if kwarg in self.finalKwargs:
                raise RuntimeError(kwarg+" already specified"
                                    +" in self.finalKwargs!"); 
            self.finalKwargs[kwarg] = kwargs[kwarg];
    def prepareFinalKwargs(self, manager, options):
        self.finalKwargs = OrderedDict();
        #handle self.kwargsAsIs 
        updateFinalKwargs(self.kwargsAsIs);
        #handle self.kwargsFromArgParse
        self.prepareFinalKwargsFromArgParse(options); 
        #now handle self.subRegisterKwargs
        self.registerSubRegisterKwargs(manager, options);
    def registerSubRegisterKwargs(manager, options):
        for kwarg in self.kwargsFromSubRegisterer:
            subRegisterName = self.valGenName+"_"+kwarg;
            self.kwargsFromSubRegisterer[kwarg].register(manager, subRegisterName, options); 
            self.finalKwargs.updateFinalKwargs({kwarg: RefVal(subRegisterName)});     
    def prepareFinalKwargsFromArgParse(self, options):
        self.assertGetArgParseArgsCalledIfNecessary(self); 
        self.assertAllArgumentNamesPresent(options);
        kwargsFromOptions = OrderedDict();
        for kwarg in self.kwargNameToArgParseName:
            argParseName = self.kwargNameToArgParseName[kwarg];
            self.updateFinalKwargs({kwarg: getattr(options, argParseName)}); 
    def assertAllArgumentNamesPresent(options):
        if len(self.kwargsFromArgParse) == 0:
            #no arguments expected from options; nothing to check
            return;
        else:
            argParseNames = self.kwargNameToArgParseName.values();
            if (options is None):
                raise RuntimeError("options object is None, but I am"
                +" expecting the following arguments to be specified"
                +" in it: "+str([x for x in argParseNames]));
            for argumentName in argParseNames:
                if (getattr(argumentName, options)==False):
                    raise RuntimeError("Expected argument "+str(argumentName)
                                        +" is missing from options object");  
    def getPrefixForArgParse(self):
        self.assertValGenNameSet();
        return self.valGenName;
    def getArgParseArgs(self):
        """
            returns an array of util.ArgParseArgument.
            Also keeps track of the generated ArgParseArgument
                for each kwarg (i.e. makes the map kwargNameToArgParseName).
        """
        prefix = self.getPrefixForArgParse();
        #I can conceive of some situations where you
        #would want no prefix...pertaining to dynamic
        #argparse parsing...but that's for later.
        prefix = "" if prefix is None else prefix+"_"; 
        self.kwargNameToArgParseName = OrderedDict();
        argParseArguments = [];
        for kwarg in self.argParseKwargs:
            argumentName = prefix+kwarg;
            argParseArgument = util.ArgParseArgument(argumentName=argumentName
                                                ,**self.argParseKwargs[kwarg]);
            self.kwargNameToArgParseName[kwarg] = argumentName; 
            argParseArguments.append(argParseArgument);
        for (kwarg, subRegisterer) in self.kwargsFromSubRegisterer.items():
            self.argParseArguments.extend(subRegisterer.getArgParseArgs(prefix=prefix+kwarg))
        return argParseArguments;
    def assertGetArgParseArgsCalledIfNecessary(self):
        if len(self.kwargsFromArgParse) > 0:
            if self.internalNameToArgParseArgs is None:
                raise RuntimeError("It looks like this Registerer"
                +" specifies some arguments to be gotten via argparse, but"
                +" you never called getArgParseArgs meaning you"
                +" couldn't have included them in any ArgumentParser...");   
    def assertPrepareNotCalled(self):
        if self.finalKwargs is not None:
            raise RuntimeError("Can't modify kwargs after prepareFinalKwargs already called");
    def assertPrepareCalled(self):
        if (self.finalKwargs is None):
            raise RuntimeError("Please call prepareFinalKwargs before calling this");
    def setKwargs(self, **kwargs):
        """
            The values provided here must be instances 
                of AbstractValProvider
            To faciliate builder pattern, this returns
                an instance of self.
        """
        self.assertPrepareNotCalled();
        for val in kwargs.values():
            if (isinstance(val, AbstractValProvider)==False):
                raise RuntimeError("The values provided here must be"
                    +" instances of AbstractValProvider");
        self.kwargsAsIs.update(kwargs);
        return self; 
    def setFixedKwargs(self, **kwargs):
        """
            Convenience function; will wrap the values 
                in FixedVal and will call setKwargs.
        """
        self.assertPrepareNotCalled();
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
        self.assertPrepareNotCalled();
        self.argParseKwargs.update(kwargs); 
        return self;
    def addArgParseArgsToParser(self, parser):
        """
            Convenience function; calls getArgParseArgs,
                adds the resulting arguments to parser.
        """
        argParseArgs = self.getArgParseArgs();
        for arg in argParseArgs:
            arg.addToParser(parser); 
    def getArgParseObject(self, description):
        """
            Convenience function; instantiates an argparse
                object with description, and calls
                addArgParseOptsToParser on it. 
        """
        parser = argparse.ArgumentParser(description=description); 
        self.addArgParseOptsToParser(parser);
        return parser;
    @abstractmethod
    def _getValGen(self, manager, options, **kwargs):
        """
            returns a function which accepts 'manager'
                and performs all the
                necessary registrations.
        """
        raise NotImplementedError(); 

class AbstractBasicValGenRegisterer(AbstractValGenRegisterer):
    @abc.abstractmethod
    def _getBasicValGen(self, **kwargs):
        """
            Get an instance of ValGenerator given **kwargs which
                all map to ValProviders.
        """ 
        raise NotImplementedError();
    def _getValGen(self, manager, valGen, options, **kwargs):
        valGen = self._getBasicValGen(**kwargs);
        return valGen;

class ParamArgGenRegisterer(AbstractBasicValGenRegisterer):
        




