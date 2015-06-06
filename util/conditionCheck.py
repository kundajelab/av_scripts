from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);

def getIndentation(indentation):
    "".join("\t" for i in xrange(indentation));

class Condition(object):
    def __init__(self):
        self.isSatisfied = None;
    def getDescription(self, indentation):
        raise NotImplementedError();
    def isSatisfied(self):
        if (self.isSatisfied == None):
            self.isSatisfied = self.computeIsSatisfied();
            assert self.isSatisfied is not None;
        return self.isSatisfied;
    def computeIsSatisfied(self):
        raise NotImplementedError();
    def getSatString(self):
        if (self.isSatisfied):
            return "(Satisfied)";
        elif (self.isSatisfied==False):
            return "(Not Satisfied)";
        else:
            raise RuntimeError("Satisfied should be set");

class ValueAmongOptions(Condition):
    def __init__(self, val, valName, supportedOptions):
        self.supportedOptions = supportedOptions;
        self.val = val;
        self.valName = valName;
    def getDescription(self, indentation):
        return getIndentation(indentation)+"{"+self.getSatString()+" value "+self.valName+" is "+str(self.val)+"; should be in "+("\t".join(str(x) for x in self.supportedOptions))+"\n}"; 
    def computeIsSatisfied(self):
        return self.val in self.supportedOptions;

class ValueIsSetInOptions(Condition):
    def __init__(self, options, valName):
        self.options = options;
        self.valName = valName; 
    def getDescription(self, indentation):
        return getIndentation(indentation)+"{"+self.getSatString()+" value "+self.valName+" must be set}";
    def computeIsSatisfied(self):
        if (hasattr(self.options,self.valName) and getattr(self.options,self.valName) is not None and getattr(self.options,self.valName) != False):
            return True;
        else:
            return False;

class Notter(Condition):
    def __init__(self, condition):
        self.condition = condition;
    def getDescription(self, indentation):
        return getIndentation(indentation)+"{"+self.getSatString()+" Following should by unsatisfied: {\n"+self.condition.getDescription(indentation+1)+"\n}";
    def computeIsSatisfied(self):
        return (self.condition.computeIsSatisfied() == False);

class ArrayCondition(Condition):
    def __init__(self, conds):
        """
            conds: array of conditions
        """
        self.conds = conds;
    def getArrayConditionString(self):
        raise NotImplementedError();
    def getDescription(self, indentation):
        return (getIndentation(indentation)+"{"+self.getSatString()+" "+self.getArrayConditionString()+" [\n"
                        +"\n".join(x.getDescription(indentation+1))
                +"]}");
    def computeIsSatisfied(self):
        raise NotImplementedError();

class Or(ArrayCondition):
    def getArrayConditionString(self):
        return "at least one of the following must be true:"
    def computeIsSatisfied(self):
        return any(x.isSatisfied() for x in self.conds);

class All(ArrayCondition):
    def getArrayConditionString(self):
        return "all of the following must be true:";
    def computeIsSatisfied(self):
        return all(x.isSatisfied() for x in self.conds);

class AtMostOne(ArrayCondition):
    def getArrayConditionString(self):
        return "at most one of the following can be true";
    def computeIsSatisfied(self):
        return sum(self.conds) <= 1;

class ExactlyOne(ArrayCondition):
    def getArrayConditionString(self):
        return "only one of the following can be true"; 
    def computeIsSatisfied(self):
        return sum(self.conds) == 1;



