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
import types; 
import copy;

CustomWarning = namedtuple("CustomWarning", ["warningType","warningMessage","stackTrace"]);

class Manager(object):
    def __init__(self, warningsHandlerFunc):
        """
            warningsHandlerFunc: takes as input a CustomWarning object
        """
        self.generatorNameToGenerator = {};
        self.warningsHandlerFunc = warningsHandlerFunc;
    def prepareNextSet(self):
        for generator in self.generatorNameToGenerator.values():
            generator.prepareNextSet(); 
    def getValForThisSet(self, valGenName):
        return self._getValGenerator(valGenName).getValForThisSet(self);
    def _getValGenerator(self, valGenName):
        return self.generatorNameToGenerator[valGenName];
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
    def getJsonableObject(self):
        return OrderedDict([
                (valGenName
                ,self._getValGenerator(valGenName).getJsonableObject())
                for valGenName in self.getTrackedValGenNames()]);
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
    def logWarning(self, warningType, warningMessage):
        self.warningsHandlerFunc(ValGenWarning(warningType=warningType
                                    ,warningMessage=warningMessage
                                    ,stackTrace=util.getStackTrace())); 

class AbstractValProvider(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getValForThisSet(self, manager=None):
        raise NotImplementedError();
    @abc.abstractmethod
    def getJsonableObject(self):
        raise NotImplementedError();

class FixedVal(AbstractValProvider):
    def __init__(self, val):
        self.val = val;
    def getValForThisSet(self, manager=None):
        return self.val; 
    def getJsonableObject(self):
        return "Fixed:"+str(self.val)

FuncAndDescription = namedtuple("FuncAndDescription", ["func", "description"]);
class RefVal(AbstractValProvider):
    def __init__(self, valGenName
                , funcAndDescription=FuncAndDescription(func=lambda x: x
                                , description="identity")):
        self.valGenName = valGenName;
        util.assertIsType(instance=funcAndDescription
                        ,theClass=FuncAndDescription
                        ,instanceVarName="funcAndDescription");
        self.funcAndDescription = funcAndDescription;
    def getValForThisSet(self, manager):
        return self.funcAndDescription.func(
                manager.getValForThisSet(self.valGenName)); 
    def getJsonableObject(self):
        return OrderedDict([("class","RefVal")
                            ,("valGenName",self.valGenName)
                            ,("func",self.funcAndDescription.description)])

class ParamValProvider(AbstractValProvider):
    def __init__(self, paramName, valProvider):
        self.paramName = paramName;
        self.valProvider = valProvider;
    def getValForThisSet(self, manager):
        return "--"+self.paramName+" "+self.valProvider.getValForThisSet(manager);
    def getJsonableObject(self):
        return OrderedDict([("param",self.paramName)
                ,("valProvider",self.valProvider.getJsonableObject())]);

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

class CustomValGenerator(AbstractValGenerator):
    __metaclass__ = abc.ABCMeta
    def __init__(self, generatorFuncAndDescription, isTracker):
        super(ValGenerator, self).__init__(isTracked=isTracker);
        util.assertIsType(instance=generatorFuncAndDescription
                        ,theClass=FuncAndDescription
                        ,instanceVarName="generatorFuncAndDescription");
        self.generatorFuncAndDescription = generatorFuncAndDescription;
    def generate(self, manager):
        return self.generatorFuncAndDescription.func(manager); 
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "CustomValGenerator")
            ("generatorFunc", self.generatorFuncAndDescription.description) 
        ]);


def getArgument_requiredIfNoDefault(parser, argName, default, **kwargs):
    util.ArgParseArgument(argumentName=argName, default=default
                        , required=(True if default else False), **kwargs);


class IValGenRegisterer(object):
    """
        I am mimicking java with an interface declaration here,
            for simplicity of documentation.
    """
    __metaclass__ = abc.ABCMeta
    def assertRequiredThingsAreSet(self):
        """
            If there are any other setters that must be called,
                can assert that they have been called using
                this function, which is called both by
                _getArgParseArgs and _register
        """
        pass;
    def _getArgParseArgs(self):
        self.assertRequiredThingsAreSet();
        return self._getArgParseArgs_core(); 
    @abc.abstractmethod
    def _getArgParseArgs_core(self):
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
    def register(manager, options):
        """
            will register a val generator. The name should
                have been set through other mecanisms.
        """
        self.assertRequiredThingsAreSet();
        self.register_core(manager, options);
    @abc.abstractmethod
    def register_core(manager, options):
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
        self._valGenName = valGenName;
    def getValGenName(self):
        return self._valGenName;
    def _assertValGenNameSet(self):
        """
            Verifies that setValGenName has been called
        """
        if (self.getValGenName() is None):
            raise RuntimeError("Need to call setValGenName before you call this");
    def register_core(self, manager, options):
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
        The method which has the needed kwargs is to be annotated
            with the kwargsHere decorator. The arguments
            'manager' and 'options' will be ignored.
    """
    methodToUse = None;
    for methodName, method in cls.__dict__.iteritems()
        if method.kwargsHere==True:
            if (methodToUse is None):
                methodToUse = method;
            else:
                raise RuntimeError("Both "+methodToUse.__name__
                    +" and "+methodName+" were annotated with"
                    +" the kwargsHere decorator in"
                    +" class "+cls.__name__);
    if methodToUse is None:
        raise RuntimeError("No method found with kwargsHere"
            +" decorator in class "+cls.__name__);
    allKwargs = methodToUse.__code__.co_varnames
    defaults = methodToUse.__defaults__;
    defaults = [] if defaults is None else defaults;
    ignoredKwargs = Set(['self', 'manager', 'options'])
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

def kwargsHere(func):
    """
        To be used to annotate the function that will
            be picked up by the class decorator
            createValidAndRequiredKwargs.
    """
    func.kwargsHere = True;
    return func;

class ParamArgGenRegisterer(IValGenRegisterer):
    def __init__(self, paramName, valGenRegisterer, actualParamPrefix=None):
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
            actualParamPrefix will be set to paramName if None
                Have this for cases where there may be param
                name conflix as is the case when a string of args
                is parsed dynamicallly by other argparsers.
        """
        self._paramName = paramName;
        self._actualParamPrefix = (paramName if actualParamPrefix
                                    is None else actualParamPrefix);
        if (isinstance(valGenRegisterer, AbstractValGenRegisterer_SettableName)==False):
            util.assertIsType(
                instance=valGenRegisterer
                ,theClass=AbstractValGenRegisterer_SettableName
                ,instanceVarName="valGenRegisterer");
        self._valGenRegisterer = valGenRegisterer;
    @property
    def paramName(self):
        return self._paramName;
    def getValGenName(self):
        """
            N.B. this refers to generator that generates
                the string including the parmeter name!
        """
        return self._paramName+"_param";
    def getValGenRegisterer(self):
        """
            N.B. this refers to the underlying val gen
                registerer!
        """
        return self._valGenRegisterer; 
    def _getArgParseArgs_core(self):
        return self._valGenRegisterer._getArgParseArgs();
    def register_core(manager, options):
        self._valGenRegisterer.setValGenName(self._paramName);
        def generatorFunc(manager):
            val = manager.getValForThisSet(self._paramName);
            return "--"+self._actualParamPrefix+" "+str(val);
        manager.registerGenerator(
                name=self.getValGenName()
                ,generator=ValGenerator(
                    generatorFuncAndDescription=
                    FuncAndDescription(
                        func=generatorFunc
                        ,description=self._paramName+" prefix")));

class ArgsJoinerValGenerator(AbstractValGenerator):
    def __init__(self, valProviders):
        for valProvider in valProviders:
            util.assertIsType(instance=valProvider
                ,theClass=ValProviders
                ,instanceVarName="valProvider");
        self.valProviders = valProviders;
    def generate(self, manager):
        vals = [valProvider.getValForThisSet(manager)
                for valProvider in self.valProviders];
        vals = [val for val in vals if val != util.UNDEF];
        return " ".join(vals);
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "ArgsJoinerValGenerator")
            ("valProviders", [
                valProvider.getJsonableObject() for valProvider in self.valProviders
            ]) 
        ]);
       
class ArgsJoinerValGenRegisterer(AbstractValGenRegisterer_SettableName):
    """
        Requires user to call setValGenName.
    """
    def __init__(self, isTracked=False):
        self.argsRegisterers = []; 
        self.isTracked=isTracked;
    def addArgRegisterers(self, **argsRegisterers):
        for argsRegisterer in argsRegisterers:
            util.assertIsType(
                instance = argsRegisterer
                ,theClass=IValGenRegisterer
                ,instanceVarName="argsRegisterer"); 
        self.argsRegisterers.extend(argsRegisterers);
        return self;
    def getArgParseArgs(self):
        toReturn = [];
        for argsRegisterer in self.argsRegisterers:
            toReturn.extend(argsRegisterer.getArgParseArgs());
        return toReturn;
    def _getValGen(manager, options):
        valProviders = []
        for argsRegisterer in argsRegisterers:
            argsRegisterer.register(manger, options);
            valProviders.append(RefVal(argsRegisterer.getValGenName()));
        return ArgsJoinerValGenerator(valProviders=valProviders);

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
    """
        static kwargs are those kwargs whose values must be accessible
            at registration time, and so they cannot come from
            a subRegisterer.
    """
    staticKwargs = Set();
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
    @classmethod
    def _checkKwargsNotInStaticKwargs(cls, **kwargs):
        if kwarg in cls.staticKwargs:
            raise RuntimeError(kwarg+" is listed as a"
            +" static kwarg among "+str(cls.staticKwargs)
            +" so you can't set it using a subRegisterer"); 
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
        self._checkKwargsNotInStaticKwargs(**kwargs);
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
            kwargs[kwarg] = util.augmentArgparseKwargsHelpWithDefault(
                                **kwargs[kwarg]
                            );
        self.argParseKwargs.update(kwargs); 
        return self;

    #################
    # Getting required arguments for argParse object
    #################
    def _getPrefixForArgParse(self):
        self._assertValGenNameSet();
        return self.valGenName;
    def _getArgParseArgs_core(self):
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
    def _getValGen(self, manager, options, **kwargs):
        valGen = self._getBasicValGen(**kwargs);
        return valGen;

class AbstractRangedValGenerator(AbstractValGenerator):
    """
        Has a simple helper funtion to check if
            min is ever > max, and if so, coerce the
            min down while providing a warning.
    """
    def __init__(self, minVal, maxVal):
        self._minVal = minVal;
        self._maxVal = maxVal;
    @property
    def maxVal(self):
        return self._maxVal;
    def minVal(self):
        return self._minVal;
    def reconcileMinAndMax(self, minVal, maxVal, manager):
        if (minVal > maxVal):
            message = "Received a min of "+str(minVal)\
                        +" and a max of "+str(maxVal)\
                        +"; wll coerce the min to be the max"
            manager.logWarning("Min-Max inconsistency", message);
            minVal = maxVal;
        return minVal, maxVal;

class RangedNumStepsValGenerator(AbstractRangedValGenerator):
    def __init__(self, minVal, maxVal, numSteps, logarithmic, roundTo, cast, **kwargs):
        super(RangedNumStepsValGenerator, self)\
            .__init__(minVal=minVal, maxVal=maxVal, **kwargs);
        self.numSteps = numSteps;
        self.logarithmic = logarithmic;
        self.roundTo = roundTo;
        self.cast = cast;
    @abc.abstractmethod
    def generate(self, manager):
        minVal = self.minVal.getValForThisSet(manager);
        maxVal = self.maxVal.getValForThisSet(manager);
        minVal, maxVal = self.reconcileMinAndMax(minVal, maxVal, manager);
        numSteps = self.numSteps.getValForThisSet(manager);
        logarithmic = self.numSteps.getValForThisSet(manager);
        roundTo = self.numSteps.getValForThisSet(manager);
        cast = self.numSteps.getValForThisSet(manager);
        return util.sampleFromNumSteps(minVal=minVal
                , maxVal=maxVal, numSteps=numSteps
                , logarithmic=logarithmic, roundTo=roundTo
                , cast=cast);  
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "RangedNumStepsValGenerator")
            ,("minVal", self.minVal.getJsonableObject())
            ,("maxVal", self.maxVal.getJsonableObject())
            ,("numSteps", self.numSteps.getJsonableObject())
            ,("logarithmic", self.logarithmic.getJsonableObject())
            ,("roundTo", self.roundTo.getJsonableObject())
            ,("cast", str(self.cast.getJsonableObject()))
        ]);


class RangedValGenRegisterer(BasicAbstractValGenRegisterer):
    def setMinArgParseKwarg(self, default, type=float):
        self._setArgParseKwargs(minVal={default=default, type=type});
        return self;
    def setMaxArgParseKwarg(self, default, type=float):
        self._setArgParseKwargs(maxVal={default=default, type=type});
        return self;

@createValidAndRequiredKwargs
class RangedNumStepsValGenRegisterer(RangedValGenRegisterer):
    def setNumStepsArgParseKwarg(self, default):
        self._setArgParseKwargs(numSteps={default=default, type=int});
        return self;
    @kwargsHere
    def _getBasicValGen(self, minVal, maxVal, logarithmic
                        , numSteps, cast=FixedVal(lambda x: x)
                        , roundTo=FixedVal(None)):
        return RangedNumStepsValGenerator(
            minVal=minVal, maxVal=maxVal
            ,numSteps=numSteps, logarithmic=logarithmic
            ,roundTo=roundTo, cast=cast);

@createValidAndRequiredKwargs
class UniformIntValGenRegisterer(RangedNumStepsValGenerator):
    @kwargsHere
    def _getBasicValGen(self, minVal, maxVal, numSteps
                            , roundTo=FixedVal(None)):
        return RangedNumStepsValGenerator(minVal=minVal
                , maxVal=maxVal, numSteps=numSteps
                , logarithmic=FixedVal(False)
                , roundTo=roundTo, cast=FixedVal(int));

class RangedStepSizeValGenerator(AbstractRangedValGenerator):
    def __init__(self, minVal, maxVal, stepSize, cast, **kwargs):
        super(RangedStepSizeValGenerator, self)\
            .__init__(minVal=minVal, maxVal=maxVal, **kwargs);
        self.stepSize = stepSize;
        self.cast = cast;
    @abc.abstractmethod
    def generate(self, manager):
        minVal = self.minVal.getValForThisSet(manager);
        maxVal = self.maxVal.getValForThisSet(manager);
        minVal, maxVal = self.reconcileMinAndMax(minVal, maxVal, manager);
        stepSize = self.stepSize.getValForThisSet(manager);
        cast = self.numSteps.getValForThisSet(manager);
        return util.sampleFromNumSteps(minVal=minVal
                , maxVal=maxVal, numSteps=numSteps
                , logarithmic=logarithmic, roundTo=roundTo
                , cast=cast);  
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "RangedStepSizeValGenerator")
            ,("minVal", self.minVal.getJsonableObject())
            ,("maxVal", self.maxVal.getJsonableObject())
            ,("stepSize", self.stepSize.getJsonableObject())
            ,("cast", str(self.cast.getJsonableObject()))
        ]);

@createValidAndRequiredKwargs
class RangedStepSizeValGenRegisterer(RangedValGenRegisterer):
    def setStepSizeArgParseKwarg(self, default, type=type):
        self._setArgParseKwargs(stepSize={default=default, type=type});
        return self;
    @kwargshere
    def _getBasicValGen(self, minVal, maxVal, stepSize
                        , cast=FixedVal(lambda x: x)):
        return RangedStepSizeValGenerator(minVal=minVal
                , maxVal=maxVal, stepSize=stepSize, cast=cast); 

class ArrSamplerValGenerator(AbstractValGenerator):
    def __init__(self, choices, **kwargs):
        super(ArrSamplerValGenerator, self).__init__(**kwargs); 
        self.choices = choices;
    def generate(self, manager):
        choices = self.choices.getValForThisSet(manager);
        return util.randomlySampleFromArr(choices); 
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "ArrSamplerValGenerator")
            ,("choices", self.choices.getJsonableObject())
        ]);

@createValidAndRequiredKwargs
class ArrSamplerValGenRegisterer(BasicAbstractValGenRegisterer):
    def setChoicesArgParseKwarg_withFullChoicesSet(self, default, fullChoicesSet, type=str):
        self._setArgParseKwargs(choices={default=default
                , nargs='+', choices=fullChoicesSet, type=type});
        return self;
    def setChoicesArgParseKwarg(self, default, type=float):
        self._setArgParseKwargs(choices={default=default
                                , nargs='+', type=type});
        return self;
    @kwargsHere 
    def _getBasicValGen(self, choices):
        return ArrSamplerValGenerator(choices=choices); 

class BinarySamplerValGenerator(AbstractValGenerator):
    def __init__(self, valIfOn, valIfOff, probOn):
        self.valIfOn = valIfOn;
        self.valIfOff = valIfOff;
        self.probOn = probOn;
    def generate(self, manager):
        probOn = self.probOn.getValForThisSet(manager);
        assert isinstance(probOn, float);
        assert probOn >= 0.0 and probOn <= 1.0
        #we want to make sure getValForThisSet is called
        #lazily; that way, if it isn't called, it
        #the corresponding val generator won't be tracked
        if random.random() < probIfTrue:
            return self.valIfOn.getValForThisSet(manager);
        else:
            return self.valIfOff.getValForThisSet(manager);
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "BinarySamplerValGenerator")
            ,("valIfOn", self.valIfOn.getJsonableObject())
            ,("valIfOff", self.valIfOff.getJsonableObject())
            ,("probOn", self.probOn.getJsonableObject())
        ]);


@createValidAndRequiredKwargs
class BinarySamplerValGenRegisterer(BasicAbstractValGenRegisterer):
    def setProbArgParseKwarg(self, default):
        self._setArgParseKwargs(probOn={default=default, type=float}); 
        return self;
    @kwargsHere
    def _getBasicValGen(self, valIfOn, valIfOff, probOn):
        return BinarySamplerValGenerator(valIfOn=valIfOn
                    ,valIfOff=valIfOff, probOn=probOn);

@createValidAndRequiredKwargs
class SetOfArrParamsArgGenRegisterers(FlexibleAbstractValGenRegisterer):
    staticKwargs=Set(["maxNumLayers"]);
    def __init__(self, isTracked=False):
        super(ArrSetsParamsValGenRegisterer).__init__(isTracked=isTracked); 
        self.arrParamArgGenRegisterers = []
    def addArrParamArgGenRegisterers(self, **arrParamArgGenRegisterers):
        for arrParamArgGenRegisterer in arrParamArgGenRegisterers:
            util.assertIsType(
                instance=argsRegisterer
                ,theClass=ParamArgGenRegisterer
                ,instanceVarName="argsRegisterer"); 
        self.arrParamArgGenRegisterers.extend(arrParamArgGenRegisterers);
        return self; #builder pattern
    def getArgParseArgs(self):
        toReturn = super(SetOfArrParamsValGenRegisterers, self).getArgParseArgs();
        for arrParamArgGenRegisterer in self.arrParamArgGenRegisterers:
            toReturn.extend(arrParamArgGenRegisterer.getArgParseArgs());
        return toReturn;
    @kwargsHere
    def _getValGen(manager, options, maxNumLayers, numLayers):
        """
            numLayers: either something fixed, eg via argparse, or
                a generator itself.
        """
        valProviders = []
        for arrParamArgGenRegisterer in self.arrParamArgGenRegisterers:
            #they are all instances of ParamArgGenRegisterer
            #so need to get the underlying valGenRegisterer
            arrParamArgGenRegisterer.getValGenRegisterer().setKwargs(
                maxNumLayers=maxNumLayers
                , numLayers=numLayers);
            arrParamArgGenRegisterer.register(manager, options);
            valProviders.append(RefVal(arrParamArgGenRegisterer.getValGenName()));
        return ArgsJoinerValGenerator(valProviders=valProviders);

class ArrValGenerator(AbstractValGenerator):
    def __init__(self, arrLen, valProvidersForEachIndex, **kwargs):
        """
            arrLen: a valProvider
            valProvidersForEachIndex: an array of valProviders, one
                for each index.
        """
        super(RangedArrValGenerator, self).__init__(**kwargs);
        self.arrLen = arrLen;
        self.valProvidersForEachIndex;
    def generate(self, manager):
        arrLen = self.arrLen.getValForThisSet(manager);
        if arrLen > len(self.valProvidersForEachIndex):
            message = "Sampled length is"\
                +" "+str(arrLen)+" but the length"\
                +" of declared valGenerators is"\
                +" "+str(len(self.valProvidersForEachIndex))\
                +". For now, will just reduce the array"\
                +" length to "+str(len(self.valProvidersForEachIndex))
            manager.logWarning("ArrayLengthInconsistency",message);
            arrLen = len(self.valProvidersForEachIndex); 
        toReturn = [];
        for i in xrange(arrLen):
            toReturn.append(self.valProvidersForEachIndex[i].getValForThisSet());    
        return toReturn;
    def getJsonableObject(self):
        return OrderedDict([
            ("class", "ArrValGenerator")
            ,("arrLen", self.arrLen.getJsonableObject())
            ,("valProvidersForEachIndex"
            , [valProvider.getJsonableObject() for valProvider
                in self.valProvidersForEachIndex])]);

def extendToListIfNot(arrLen, val):
    if isinstance(val, list)==False or len(val)==1:
        if (isinstance(val, list)):
            val = val[0];
        val = [val]*len(arrLen);
    else:
        if (len(val) < arrLen):
            raise RuntimeError("Array of length "+str(arrLen)
                +" expected but got array of len "+str(len(val)));
    return val;

def interpretArrVals(arrVals, indexToValGenName, functionUsingPrev, funcDescription):
    """
        Interprets keywords like 'prev' if applicable,
            otherwise casts numbers to floats
        functionUsingPrev is a function that takes as input a value
            and returns a function of what will be the previous
            argument.
    """ 
    interpretedVals = []
    for i,val in enumerate(arrVals):
        if isinstance(val, "str"):
            if "prev-" in val:
                prevConstraint = True
                val = val.split("-")[1] 
        val = float(val); #errors out if cast fails
        if prevConstraint == False:
            interpretedVals.append(FixedVal(val)); 
        else:
            if (i == 0):
                raise RuntimeError("prev keyword can't apply to"
                    +" the first position");
            interpretedVals.append(
                RefVal(valGenName=indexToValGenName
                        ,funcAndDescription=FuncAndDescription(
                            func=functionUsingPrev(val)
                            ,description=funcDescription+"("+str(val)+")")));  
def conservativeMinConstraintUsingPrev(val):
    #to be used in conjunction with interpretArrVals
    #the more conservative 'minimum' requires taking a max.
    return lambda x: max(x, val);
def conservativeMaxConstraintUsingPrev(val):
    #to be used in conjunction with interpretArrVals
    #the more conservative 'maximum' requires taking a min.
    return lambda x: min(x, val); 

def assertAllOrNone(attrs, vals):
    allNone = all([val is not None for val in vals]);
    noneNone = all([val is None for val in vals]);
    if (not (allNone or noneNone)):
        raise AssertionError("Either all should be none or"
            +" none should be none, but values are"
            +" "+str([(attr, val) for (attr,val) in zip(attrs, vals)]));

class BinaryArrParseKwargMixin(object):
    staticKwargs=Set(["maxNumLayers", "probsOn", "valsIfOff"]);
    def setProbsOnParseKwarg(self, default, type=float):
        assert default >= 0 and default <= 1;
        self._setArgParseKwargs(probsOn={default=default, type=type, nargs='+'});
        return self;
    def setValsIfOffParseKwarg(self, default):
        self._setArgParseKwargs(valsIfOff={default=default, nargs='+'});
        return self;
    def setNumLayersParseKwarg(self):
        self._setArgParseKwargs(numLayers={type=int, required=True});
        return self;
    def _getMaxNumLayers(self, numLayers, manager):
        if (isinstance(numLayers, FixedVal)):
            return numLayers.getValForThisSet(manager=None);  
        elif (isinstance(numLayers, RefVal)):
            #the registration should have already been done via
            #self._prepareFinalKwargs
            numLayersValGenerator = manager._getValGenerator(numLayers.valGenName);
            if (isinstance(numLayersValGenerator, AbstractRangedValGenerator)):
                return numLayersValGenerator.maxVal;
            else:
                raise RuntimeError("Unsure how to determine maxVal for"
                        +str(numLayersValGenerator.__class__));
        else:
            raise RuntimeError("Unsure how to determine maxVal for"
                    +str(numLayers.__class__));

@createValidAndRequiredKwargs
class BinaryArrValGenRegisterer(FlexibleAbstractValGenRegisterer
                                , BinaryArrParseKwargMixin):
    staticKwargs = [x for x in BinaryArrParseKwargMixin.staticKwargs]+["valsIfOn"]
    def setValsIfOnParseKwarg(self, default):
        self._setArgParseKwargs(valsIfOn={default=default, nargs='+'});
        return self;
    @kwargsHere
    def _getValGen(manager, options, numLayers
                    , probsOn, valsIfOn, valsIfOff):
        maxNumLayers = self._getMaxNumLayers(numLayers, manager);
        #probOn, valsIfOn, valsIfOff are needed at
        #registeration time so the val should be providable
        #even without a manager argument.
        probsOn = probsOn.getValForThisSet(manager=None); 
        valsIfOn = valsIfOn.getValForThisSet(manager=None);
        valsIfOff = valsIfOff.getValForThisSet(manager=None);
        
        #def interpretArrVals(arrVals, indexToValGenName, functionUsingPrev):
        parentValGenName = self.getValGenName();
        indexToValGenName = lambda i: parentValGenName+"_"+str(i);
        probsOn = extendToListIfNot(arrLen=maxNumLayers, val=probsOn);  
        valsIfOn = extendToListIfNot(arrLen=maxNumLayers, val=valsIfOn);
        valsIfOff = extendToListIfNot(arrLen=maxNumLayers, val=valsIfOff); 
        
        valProvidersForEachIndex = []
        for i in xrange(maxNumLayers):
            valGeneratorForIndexName = indexValGenName(i); 
            valGenRegisterer = BinarySamplerValGenRegisterer()\
                    .setFixedKwargs(valIfOn=valsIfOn[i])
                    .setFixedKwargs(valIfOff=valsIfOff[i])\
                    .setFixedKwargs(probOn=probsOn[i])
            valGenRegisterer.setValGenName(indexValGenName); 
            valGenRegisterer.register(manager, options);
            valProvidersForEachIndex.append(RefVal(valGeneratorForIndexName));
        return ArrValGenerator(arrLen=numLayers
                    ,valProvidersForEachIndex=valProvidersForEachIndex);

def assertAttrSet(obj, attrName, setterName=None):
    if (setterName is None):
        setterName = "set"+attrName.capitalize();
    if (hasattr(obj, attr)==False):
        raise RuntimeError(attr+" not set...maybe call "+setterName);

@createValidAndRequiredKwargs
class OptionallyBinaryRangedArrValGenRegisterer(FlexibleAbstractValGenRegisterer
                                                , BinaryArrParseKwargMixin):
    staticKwargs=Set(["minVals", "maxVals"]
                    +[x for x in BinaryArrParseKwargMixin.staticKwargs]);
    def assertRequiredThingsAreSet(self): 
        assertAttrSet(self, 'singleRangedValGenRegisterer');
    def setSingleRangedValGenRegisterer(self, singleRangedValGenRegisterer):
        """
            singleRangedValGenRegisterer: a registerer for a AbstractRangedValGenerator
                that only needs a min and a max. So, in other words,
                it should have logarithmic, roundTo and cast fixed (they may
                be obtained from an argparse object
                It will be deepcopied as needed.
        """
        util.assertIsType(instance=singleRangedValGenRegisterer
                        ,theClass=RangedValGenRegisterer
                        ,instanceVarName="singleRangedValGenRegisterer");
        self.singleRangedValGenRegisterer=singleRangedValGenRegisterer;
    def setMinValsParseKwarg(self, default, type=float):
        self._setArgParseKwargs(minVals={default=default, type=type, nargs='+'});
        return self;
    def setMaxValsParseKwarg(self, default, type=float):
        self._setArgParseKwargs(maxVals={default=default, type=type, nargs='+'});
        return self;
    def getArgParseArgs(self):
        argParseArgs = super(RangedArrValGenRegisterer, self).getArgParseArgs();
        #set the val gen name to the val gen name of this in order to
        #get the argument prefixes to be the same...a bit hacky, sigh.
        self.singleRangedValGenRegisterer.setValGenName(self.getValGenName());
        argParseArgs.extend(self.singleRangedValGenRegisterer.getArgParseArgs());
        self.singleRangedValGenRegisterer.setValGenName(None);
        return argParseArgs;
    @kwargsHere
    def _getValGen(manager, options, numLayers
                    , minVals, maxVals
                    , probsOn=FixedVal(None)
                    , valsIfOff=FixedVal(None)):
        """
            probOn: optional; probability of even using
                the range sampler for each index. If specified,
                then valsIfOff (which indicates what to use
                if sampled false) must also be specified.
        """
        #minVals, maxVals
        #probOfSample and valsIfOff are needed at
        #registeration time so the val should be providable
        #even without a manager argument.
        maxNumLayers = self._getMaxNumLayers(numLayers, manager);
        minVals = minVals.getValForThisSet(manager=None);
        maxVals = maxVals.getValForThisSet(manager=None); 
        probsOn = probsOn.getValForThisSet(manager=None); 
        valsIfOff = valsIfOff.getValForThisSet(manager=None);
        util.assertAllOrNone(['probsOn', 'valsIfOff']
                            , [probsOn, valsIfOff]); 
        
        #def interpretArrVals(arrVals, indexToValGenName, functionUsingPrev):
        parentValGenName = self.getValGenName();
        indexToValGenName = lambda i: parentValGenName+"_"+str(i);
    
        minVals = interpretArrVals(
                    arrVals=extendToListIfNot(arrLen=maxNumLayers, val=minVals)
                    ,indexToValGenName=indexValGenName
                    ,functionUsingPrev=conservativeMinConstraintUsingPrev
                    ,funcDescription="conservativeMinConstraintUsingPrev");
        maxVals = interpretArrVals(
                    arrVals=extendToListIfNot(arrLen=maxNumLayers, val=maxVals)
                    ,indexValGenName=indexValGenName
                    ,functionUsingPrev=conservativeMaxConstraintUsingPrev
                    ,funcDescription="conservativeMaxConstraintUsingPrev");
        probsOn = None if probsOn is None else\
                    extendToListIfNot(arrLen=maxNumLayers, val=probsOn); 
        valsIfOff = None if valsIfOff is None else\
                    extendToListIfNot(arrLen=maxNumLayers, val=valsIfOff); 
        
        valProvidersForEachIndex = [] 
        for i in xrange(maxNumLayers):     
            #fill in the missing arguments for the val generator
            rangeValGenRegisterer = copy.deepcopy(self.singleRangedValGenRegisterer);
            rangeValGenRegisterer.setKwargs(
                minVal=minVals[i], maxVals=maxVals[i]); 
            
            valGeneratorForIndexName = indexValGenName(i); 
            
            if (probsOn is None):
                valGenRegisterer = rangeValGenRegisterer;
            else:
                valGenRegisterer = BinarySamplerValGenRegisterer()\
                        .setKwargsFromSubRegisterers(valIfOn=rangeValGenRegisterer)\
                        .setFixedKwargs(valIfOff=valsIfOff[i])\
                        .setFixedKwargs(probOn=probsOn[i])
                
            valGenRegisterer.setValGenName(indexValGenName); 
            valGenRegisterer.register(manager, options);
            
            #Having registered the generator for the index,
            #keep track of a reference to it.
            valProvidersForEachIndex.append(RefVal(valGeneratorForIndexName));
        return ArrValGenerator(arrLen=numLayers
                    ,valProvidersForEachIndex=valProvidersForEachIndex);

@createValidAndRequiredKwargs
class TypeAndSubparamsValGenRegisterer(FlexibleAbstractValGenRegisterer):
    def __init__(self, allPossibleTypes, **kwargs):
        """
            allPossibleTypes needs to be linked to the valGenRegisterer
                that is provided for typeValGenRegisterer (specific case
                in mind: it is the same as the 'choices' provided to
                setChoicesArgParseKwarg_withFullChoicesSet for
                ArrSamplerValGenRegisterer. 
        """
        super(TypeAndSubparamsValGenRegisterer, self).__init__(**kwargs);
        self.allPossibleTypes = allPossibleTypes;
    def assertRequiredThingsAreSet(self):
        assertAttrSet(self, 'typeValGenRegisterer');
        assertAttrSet(self, 'chosenTypeToSubOptsValGenRegisterer');
    def setTypeChooserValGenRegisterer(self, typeValGenRegisterer):
        util.assertIsType(instance=typeValGenRegisterer
                            ,theClass=ParamArgGenRegisterer
                            ,instanceVarName="typeValGenRegisterer");
        self.typeValGenRegisterer = typeValGenRegisterer;
    def setChosenTypeToSubOptsValGenRegisterer(self
            , chosenTypeToSubOptsValGenRegisterer):
        self.chosenTypeToSubOptsValGenRegisterer =\
                chosenTypeToSubOptsValGenRegisterer;
    def _getArgParseArgs_core(self):
        argParseArgs = super(TypeAndSubparamsValGenRegisterer, self)\
                                                  .getArgParseArgs();
        argParseArgs.extend(self.typeValGenRegisterer\
                                        ._getArgParseArgs());
        for aType in self.allPossibleTypes:
            #augh...the param prefixes need to be different from the argparse prefixes... 
  
        #set the val gen name to the val gen name of this in order to
        #get the argument prefixes to be the same...a bit hacky, sigh.
        self.typeValGenRegisterer.setValGenName(self.getValGenName());
        argParseArgs.extend(self.singleRangedValGenRegisterer.getArgParseArgs());
        self.singleRangedValGenRegisterer.setValGenName(None);
        return argParseArgs;
    @kwargsHere
    def _getValGen(manager, options):
        #register     
        




        """
        #probOfSample and valsIfOff are needed at
        #registeration time so the val should be providable
        #even without a manager argument.
        maxNumLayers = self._getMaxNumLayers(numLayers, manager);
        probsOn = probsOn.getValForThisSet(manager=None); 
        valsIfOn = valsIfOn.getValForThisSet(manager=None);
        valsIfOff = valsIfOff.getValForThisSet(manager=None);
        
        #def interpretArrVals(arrVals, indexToValGenName, functionUsingPrev):
        parentValGenName = self.getValGenName();
        indexToValGenName = lambda i: parentValGenName+"_"+str(i);
        probsOn = extendToListIfNot(arrLen=maxNumLayers, val=probsOn);  
        valsIfOn = extendToListIfNot(arrLen=maxNumLayers, val=valsIfOn);
        valsIfOff = extendToListIfNot(arrLen=maxNumLayers, val=valsIfOff); 
        
        valProvidersForEachIndex = []
        for i in xrange(maxNumLayers):
            valGeneratorForIndexName = indexValGenName(i); 
            valGenRegisterer = BinarySamplerValGenRegisterer()\
                    .setFixedKwargs(valIfOn=valsIfOn[i])
                    .setFixedKwargs(valIfOff=valsIfOff[i])\
                    .setFixedKwargs(probOn=probsOn[i])
            valGenRegisterer.setValGenName(indexValGenName); 
            valGenRegisterer.register(manager, options);
            valProvidersForEachIndex.append(RefVal(valGeneratorForIndexName));
        return ArrValGenerator(arrLen=numLayers
                    ,valProvidersForEachIndex=valProvidersForEachIndex);
        """
    def _getAllPossibleTypes(manager, typeValGenerator):
        """
            Given the typeValGenerator, get the full set of possible
                types that could be generated. Note that this can
                only be called after typeValGenRegisterer is
                registered, i.e. it is not available when the
                arguments are being provided to the argParse.
        """ 
        raise NotImplementedError(); #TODO

#to add: optimizer example 

