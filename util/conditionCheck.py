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
    return "".join("\t" for i in xrange(indentation));

class Condition(object):
    def __init__(self):
        self.isSatisfied = None;
    def getDescription(self, indentation):
        raise NotImplementedError();
    def getIsSatisfied(self):
        if (self.isSatisfied == None):
            self.isSatisfied = self.computeIsSatisfied();
            assert self.isSatisfied is not None;
        return self.isSatisfied;
    def computeIsSatisfied(self):
        raise NotImplementedError();
    def getSatString(self):
        if (self.getIsSatisfied()):
            return "(Satisfied)";
        elif (self.getIsSatisfied()==False):
            return "(Not Satisfied)";
        else:
            raise RuntimeError();

class ValueAmongOptions(Condition):
    def __init__(self, val, valName, supportedOptions):
        self.supportedOptions = supportedOptions;
        self.val = val;
        self.valName = valName;
        super(ValueAmongOptions,self).__init__(); 
    def getDescription(self, indentation):
        return getIndentation(indentation)+"{"+self.getSatString()+" value "+self.valName+" is "+str(self.val)+"; should be in "+("\t".join(str(x) for x in self.supportedOptions))+"\n}"; 
    def computeIsSatisfied(self):
        return self.val in self.supportedOptions;

class ValueIsSetInOptions(Condition):
    def __init__(self, options, valName):
        self.options = options;
        self.valName = valName;
        super(ValueIsSetInOptions,self).__init__(); 
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
        super(Notter,self).__init__(); 
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
        super(ArrayCondition,self).__init__(); 
    def getArrayConditionString(self):
        raise NotImplementedError();
    def getDescription(self, indentation):
        return (getIndentation(indentation)+"{"+self.getSatString()+" "+self.getArrayConditionString()+" [\n"
                        +"\n".join(x.getDescription(indentation+1) for x in self.conds)
                +"]}");
    def computeIsSatisfied(self):
        raise NotImplementedError();

class Or(ArrayCondition):
    def getArrayConditionString(self):
        return "at least one of the following must be true:"
    def computeIsSatisfied(self):
        return any(x.getIsSatisfied() for x in self.conds);

class All(ArrayCondition):
    def getArrayConditionString(self):
        return "all of the following must be true:";
    def computeIsSatisfied(self):
        return all(x.getIsSatisfied() for x in self.conds);

class AtMostOne(ArrayCondition):
    def getArrayConditionString(self):
        return "at most one of the following can be true";
    def computeIsSatisfied(self):
        return sum(self.conds) <= 1;

class ExactlyOne(ArrayCondition):
    def getArrayConditionString(self):
        return "only one of the following can be true"; 
    def computeIsSatisfied(self):
        return sum(x.getIsSatisfied() for x in self.conds) == 1;

if __name__ == "__main__":
    class DummyClass(object):
        pass;
    options = DummyClass();
    options.val1 = "abcd";
    check1 = ValueIsSetInOptions(options, "val1");
    check2 = ValueIsSetInOptions(options, "val2");
    check3 = Notter(check2);
    check4 = All([check1, check2]);
    check5 = ExactlyOne([check1, check3, check2]);
    print("check1",check1.getIsSatisfied());
    print("check4",check4.getDescription(0));
    print("check4",check4.getIsSatisfied());
    print("check5", check5.getDescription(0));
    


  

