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
from sets import Set

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
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def _getArgParseArgs(self):
        """
            return instances of util.ArgParseArgument
            return any arguments needed to do the registeration to an
            ArgumentParser object, which is used to create the
            options object that is passed to register(manager, options).
        """
        raise NotImplementedError();
    def addArgParseArgsToParser(self, parser):
        """
            Convenience function; calls getArgParseArgs,
                adds the resulting arguments to parser.
        """
        argParseArgs = self._getArgParseArgs();
        for arg in argParseArgs:
            arg.addToParser(parser); 
    @abc.abstractmethod
    def register(manager, options):
        """
            will register a val generator. The name should
                have been set through other mecanisms.
        """
        raise NotImplementedError();
    @abc.absractmethod
    def getValGenName(self):
        raise NotImplementedError();

class AbstractValGenRegisterer_SettableName(IValGenRegisterer):
    """
        Like parent, but exposes settable valGenName
    """ 
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self._valGenName = None;
    def setValGenName(self, valGenName):
        assert isinstance(valGenName, str);
        self._valGenName = valGenName;
    def getValGenName(self):
        return self._valGenName;
    def _assertValGenNameSet(self):
        """
            Verifies that setValGenName has been called
        """
        if (self.getValGenName() is None):
            raise RuntimeError("Need to call setValGenName before you call this");
    def register(self, manager, options):
        """
            Will make sure that the val generator name has been set.
            Will then call _getValGen(manager, options, **self._finalKwargs) 
                and will register the returned generator.
        """
        self._assertValGenNameSet();
        valGen = self._getValGen(manager, options); 
        manager.registerGenerator(name=self.valGenName, generator=valGen);
    @abstractmethod
    def _getValGen(self, manager, options):
        """
            returns a function which accepts 'manager'
                and performs all the
                necessary registrations.
        """
        raise NotImplementedError();

def createValidAndRequiredKwargs(cls):
    """
        This is a decorator intended to work in conjunction
            with FlexibleAbstractValGenRegisterer, to
            create a set that can be used for checking whether
            kwargs that are flexibly set are in fact valid.
        It also determines those kwargs which are required,
            which will be used to throw an error if those
            kwargs are never set.         
    """
    allKwargs = cls.func.__code__.co_varnames
    defaults = cls.func.__defaults__;
    defaults = [] if defaults is None else defaults;
    ignoredKwargs = Set(['self'])
    validKwargs = Set()
    requiredKwargs = []
    for i,kwarg in enumerate(allKwargs):
        if kwarg not in ignoredKwargs:
            validKwargs.add(kwarg)
            if i < len(allKwargs)-(len(defaults)):
                requiredKwargs.append(kwarg)
    cls.validKwargs = validKwargs
    cls.requiredKwargs = requiredKwargs
    return cls

@createValidAndRequiredKwargs
class FlexibleAbstractValGenRegisterer(AbstractValGenRegisterer_SettableName):
    __metaclass__ = abc.ABCMeta
    """
        Philosophy: define a function, _getValGen, which
            takes (manager, options, **kwargs) as input,
            where **kwargs are all valProviders, and returns a ValGenerator
            to be registered with the name valGenName (set with setValGenName).
            Note that this function does not do the registering,
            but it may register dependent valGens that aren't going to be
            registered by other mechanisms.
        _getValGen takes multiple kwargs as input. The values of these
            kwargs are specified using the following functions:
            setKwargs, setFixedKwargs, setArgParseKwargs, setKwargsFromSubRegisterers.
            Those functions all return 'self' so can be chained via the builder pattern.
            Then, when register is called, _getValGen will be called and registered.
        setKwargsFromSubRegisterers: when register(manager, options) is called,
            _getValGen will be called, in addition to the register(...) function of
            any subRegisterers provided by setKwargsFromSubRegisterers.
        The register function will call '_prepareFinalKwargs'. It compiles
            all the information that was specified via the setKwarg functions above.
            _prepareFinalKwargs takes an options object, generated via argparse.
        If some kwargs were specified via setArgParseKwargs, it is necessary to call
            getArgParseArgs at some point and apply the represented arguments to an
            ArgumentParse object.
    """
    def __init__(self):
        super(self, FlexibleAbstractValGenRegisterer).__init__();
        self._kwargsAsIs = OrderedDict();
        self._kwargsFromArgParse = OrderedDict();
        self._kwargNameToArgParseName = None;
        self._kwargsFromSubRegisterer = OrderedDict();
        self._finalKwargs = None;
        self._valGenName=None;

    ##############
    # valGen production
    ##############
    def _getValGen(self, manager, options):
        """
            Will call _prepareFinalKwargs to get the full set of kwargs
                needed by _getValGenWithKwargs, stored in self._finalKwargs
        """
        self._prepareFinalKwargs(manager, options);
        return self._getValGenWithKwargs(manager, options, **self._finalKwargs); 
    #TODO: create a decorator which looks at the **kwargs
    #listed here and makes them attributes of the class that
    #can then be used for sanity checking...
    def _getValGenWithKwargs(self, manager, options, **kwargs):
        raise NotImplementedError();

    ################
    # Kwarg setting!
    ################
    def _updateFinalKwargs(self, kwargs):
        """
            Will update _finalKwargs and warn you if you appear to be
                attempting to overwrite a previously set kwarg.
            Note that if you want to handle defaults, you should NOT
                handle them by pre-specifing them in _finalKwargs in
                the init method or something; rather, they should be
                specified as defaults in the signature of _getValGen
        """
        for kwarg in kwargs:
            if kwarg in self._finalKwargs:
                raise RuntimeError(kwarg+" already specified"
                                    +" in self._finalKwargs!"); 
            self._finalKwargs[kwarg] = kwargs[kwarg];
    @classmethod
    def _checkIfKwargsAreValid(cls, **kwargs):
        if (hasattr(cls, "validKwargs")==False):
            raise RuntimeError(cls.__Name__+" does not appear to"
                +" have validKwargs set...did you specify the"
                +" createValidAndRequiredKwargs decorator for"
                +" the class?"); 
        for kwarg in kwargs:
            if kwarg not in cls.validKwargs:
                raise RuntimeError(kwarg+" is not in"
                    +" validKwargs; the validKwargs are:"
                    +" "+str(cls.validKwargs)); 
    def setKwargs(self, **kwargs):
        """
            This is the simplest way of setting the kwargs that
                will be used by _getValGen. The values here are assumed
                to be instances of AbstractValProvider. I do that
                because it introduces a lot of flexibility if this
                value is used by the valGenerator at generate time.
                Technically all values not used at generate time will
                be fixed, but differentiating between those inputs that
                will be used at create time and those that will only be
                used at generate time a distinction that
                just introduces code overhead; that's why I just ask that
                everything is an instance of AbstractValProvider
            To faciliate builder pattern, this returns
                an instance of self.
        """
        self._checkIfKwargsAreValid(**kwargs);
        self._assertPrepareNotCalled();
        for kwargs in kwargs:
            util.assertIsType(
                instance=kwargs[kwarg]
                ,theClass=AbstractValProvider
                ,instanceVarName=kwarg);
        self._kwargsAsIs.update(kwargs);
        return self; 
    def setFixedKwargs(self, **kwargs):
        """
            Convenience function; will wrap the values 
                in FixedVal and will call setKwargs.
        """
        self._checkIfKwargsAreValid(**kwargs);
        self._assertPrepareNotCalled();
        self.kwargsForRegister.update(
            dict([(x, FixedVal(kwargs[x])) for x in kwargs]));
        return self;
    def setKwargsFromSubRegisterers(self, **kwargs):
        self._checkIfKwargsAreValid(**kwargs);
        for kwarg in kwargs:
            util.assertIsType(instance=kwargs[kwarg]
                            ,theClass=IValGenRegisterer
                            ,instanceVarName=kwarg);
        self._kwargsFromSubRegisterer.update(kwargs);  
        return self
    def _setArgParseKwargs(self, **kwargs):
        """
            Any values which you want to user to provide at the command
                line via an argument parser get be specified here.
            key: argument name (argument needed for _register)
            value: argparse kwargs MINUS the argument name
            I am putting an _ before this (to indicate it should be
                private) because I think that if you are expecting
                this to be called, you should define a helper function
                for individual kwargs that specifies most of the stuff for
                the user (eg: type, nargs) and then calls this.
        """
        self._checkIfKwargsAreValid(**kwargs);
        self._assertPrepareNotCalled();
        for kwarg in kwargs:
            util.assertIsType(instance=kwargs[kwarg]
                             ,theClass=dict
                             ,instanceVarName=kwarg); 
        self.argParseKwargs.update(kwargs); 
        return self;

    #################
    # Getting required arguments for argParse object
    #################
    def _getPrefixForArgParse(self):
        self._assertValGenNameSet();
        return self.valGenName;
    def _getArgParseArgs(self):
        """
            returns an array of util.ArgParseArgument.
            Also keeps track of the generated ArgParseArgument
                for each kwarg (i.e. makes the map _kwargNameToArgParseName).
        """
        prefix = self._getPrefixForArgParse();
        #I can conceive of some situations where you
        #would want no prefix...pertaining to dynamic
        #argparse parsing...but that's for later.
        prefix = "" if prefix is None else prefix+"_"; 
        self._kwargNameToArgParseName = OrderedDict();
        argParseArguments = [];
        for kwarg in self.argParseKwargs:
            argumentName = prefix+kwarg;
            argParseArgument = util.ArgParseArgument(argumentName=argumentName
                                                ,**self.argParseKwargs[kwarg]);
            self._kwargNameToArgParseName[kwarg] = argumentName; 
            argParseArguments.append(argParseArgument);
        for (kwarg, subRegisterer) in self._kwargsFromSubRegisterer.items():
            self.argParseArguments.extend(subRegisterer.getArgParseArgs(prefix=prefix+kwarg))
        return argParseArguments;
    def _assertGetArgParseArgsCalledIfNecessary(self):
        if len(self._kwargsFromArgParse) > 0:
            if self.internalNameToArgParseArgs is None:
                raise RuntimeError("It looks like this Registerer"
                +" specifies some arguments to be gotten via argparse, but"
                +" you never called getArgParseArgs meaning you"
                +" couldn't have included them in any ArgumentParser...");   

    ################
    # Kwarg preparation after setting
    ################
    @classmethod
    def _checkAllKwargsAreSet(cls, **kwargs):
        if (hasattr(cls, "requiredKwargs")==False):
            raise RuntimeError(cls.__Name__+" does not appear to"
                +" have requiredKwargs set...did you specify the"
                +" createValidAndRequiredKwargs decorator for"
                +" the class?"); 
        for kwarg in cls.requiredKwargs:
            if kwarg not in kwargs:
                raise RuntimeError("Required kwarg "+str(kwarg)
                    +" was not specified!");
    def _prepareFinalKwargs(self, manager, options):
        """
            collates arguments that were:
                - provided directly using setKwargs or setFixedKwargs
                - to be extracted from the options object, which has
                    been created from an ArgumentParser that had
                    addArgParseArgsToParser called on it.
                - to come from a valGenerator that needs to be registered
                    and referenced.
        """
        self._finalKwargs = OrderedDict();
        #handle self._kwargsAsIs 
        self._updateFinalKwargs(self._kwargsAsIs);
        #handle self._kwargsFromArgParse
        self._prepareFinalKwargsFromArgParse(options); 
        #now handle self.subRegisterKwargs
        self._registerSubRegisterKwargs(manager, options);
        self._checkAllKwargsAreSet(**self._finalKwargs);
    def _assertPrepareNotCalled(self):
        if self._finalKwargs is not None:
            raise RuntimeError("Can't modify kwargs after _prepareFinalKwargs already called");
    def _assertPrepareCalled(self):
        if (self._finalKwargs is None):
            raise RuntimeError("Please call _prepareFinalKwargs before calling this");
    def _registerSubRegisterKwargs(manager, options):
        """

        """
        for kwarg in self._kwargsFromSubRegisterer:
            subRegisterName = self.valGenName+"_"+kwarg;
            self._kwargsFromSubRegisterer[kwarg].setValGenName(subRegisterName);
            self._kwargsFromSubRegisterer[kwarg].register(manager, subRegisterName, options); 
            self._updateFinalKwargs({kwarg: RefVal(subRegisterName)});     
    def _prepareFinalKwargsFromArgParse(self, options):
        self._assertGetArgParseArgsCalledIfNecessary(self); 
        self._assertAllArgumentNamesPresent(options);
        kwargsFromOptions = OrderedDict();
        for kwarg in self._kwargNameToArgParseName:
            argParseName = self._kwargNameToArgParseName[kwarg];
            self._updateFinalKwargs({kwarg: getattr(options, argParseName)}); 
    def _assertAllArgumentNamesPresent(options):
        if len(self._kwargsFromArgParse) == 0:
            #no arguments expected from options; nothing to check
            return;
        else:
            argParseNames = self._kwargNameToArgParseName.values();
            if (options is None):
                raise RuntimeError("options object is None, but I am"
                +" expecting the following arguments to be specified"
                +" in it: "+str([x for x in argParseNames]));
            for argumentName in argParseNames:
                if (getattr(argumentName, options)==False):
                    raise RuntimeError("Expected argument "+str(argumentName)
                                        +" is missing from options object");  

class BasicAbstractValGenRegisterer(FlexibleAbstractValGenRegisterer):
    """
        Philsophy: when all the arguments needed at creation-time
            are the same as the arguments needed at generation-time,
            use this class.
    """
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

class ParamArgGenRegisterer(IValGenRegisterer):
    def __init__(self, paramName, valGenRegisterer):
        """
            The reason why I'm not having either
                paramName or valGenRegisterer handled
                through the default mechanism is that they
                both have to be handled in ways that are
                not trivially supported by the mechanisms
                of AbstractValGenRegisterer; in particular,
                paramName should be the name passed to
                valGenRegisterer, and this registerer should
                have the name "paramGen"+blah and should
                probably also be untracked.                
            valGenRegisterer should be an instance of
                AbstractValGenRegisterer_SettableName
        """
        self._paramName = paramName;
        if (isinstance(valGenRegisterer, AbstractValGenRegisterer_SettableName)==False):
            util.assertIsType(
                instance=valGenRegisterer
                ,theClass=AbstractValGenRegisterer_SettableName
                ,instanceVarName="valGenRegisterer");
        self._valGenRegisterer = valGenRegisterer;
    @property
    def paramName(self):
        return self._paramName;
    def _getArgParseArgs(self):
        return self._valGenRegisterer._getArgParseArgs();
    def register(manager, options):
        self._valGenRegisterer.setValGenName(self._paramName);
       
class ArgsJoiner(AbstractValGenRegisterer_SettableName):
    """
        Requires user to call setValGenName.
    """
    def __init__(self):
        self.argsRegisterers = []; 
    def addArgRegisterers(self, **argsRegisterers):
        for argsRegisterer in argsRegisterers:
            util.assertIsType(
                instance = argsRegisterer
                ,theClass=IValGenRegisterer
                ,instanceVarName="argsRegisterer"); 
        self.argsRegisterers.extend(argsRegisterers);
    def getArgParseArgs(self):
        toReturn = [];
        for argsRegisterer in self.argsRegisterers:
            toReturn.extend(argsRegisterer.getArgParseArgs());
        return toReturn;
    def _getValGen(manager, options):
        for argsRegisterer in argsRegisterers:
            argsRegisterer.register(manger, options); 

  



