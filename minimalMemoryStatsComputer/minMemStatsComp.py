
#assuming the distributions we are finding stats
#for are one-dimensional, for now.
class IterativeStatsFinder(object):
    """
        Abstract class. Pass in values with .process(num)
        and then call finalise(self, **kwargs) when done
    """
    def __init__(self, name):
        self.name = name;
        self.numExamplesSeen = 0;
    def process(self, num):
        self.numExamplesSeen += 1;
    def finalise(self, **kwargs):
        raise NotImplementedError();
    def getVal(self):
        if hasattr(self, 'val') == False:
            raise "No attribute val; have you called finalise?";
        return self.val;
    def getFinderType():
        if hasattr(self, 'statsComputerType') == False:
            raise "statsComputerType not defined for this class";
        return self.statsComputerType;

class MeanFinder(IterativeStatsFinder):
    statsComputerType="Mean";
    def __init__(self, name):
        super(MeanFinder, self).__init__(name);
        self.total = 0;
    def process(self, num):
        super(MeanFinder, self).process(num);
        self.total += num;
    def finalise(self, **kwargs):
        self.val = float(self.total)/self.numExamplesSeen;

class VarianceFinder(IterativeStatsFinder):
    statsComputerType="Variance";
    def __init__(self, name):
        super(VarianceFinder, self).__init__(name);
        self.meanFinder = MeanFinder(name+"_meanFinder");
        self.meanSquareFinder = MeanFinder(name+"_meanSquareFinder");
        self.squaredTotal = 0;
    def process(self, num):
        super(VarianceFinder, self).process(num);
        self.meanFinder.process(num);
        self.meanSquareFinder.process(num**2);
    def finalise(self, **kwargs):
        self.meanFinder.finalise();
        self.meanSquareFinder.finalise();
        self.val = float(self.meanSquareFinder.getVal() - (self.meanFinder.getVal()**2));

class SdevFinder(IterativeStatsFinder):
    statsComputerType = "StandardDeviation"
    def __init__(self, name):
        super(SdevFinder, self).__init__(name);
        self.varianceFinder = VarianceFinder(name+"_varianceFinder");
    def process(self, num):
        super(SdevFinder, self).process(num);
        self.varianceFinder.process(num);
    def finalise(self, **kwargs):
        self.varianceFinder.finalise();
        self.val = self.varianceFinder.getVal()**(0.5);

class CountNumSatisfyingCriterion(IterativeStatsFinder):
    def __init__(self, name, criterion, statsComputerType, percentIncidence=True):
        """
            criterion is a function that takes as argument 'num'
        """
        super(CountNumSatisfyingCriterion, self).__init__(name);
        self.criterion = criterion;
        self.numSatisfying = 0;
        self.statsComputerType = statsComputerType;
        self.percentIncidence = percentIncidence;
        if (self.percentIncidence):
            self.statsComputerType += "_percentIncidence";
    def process(self, num):
        super(CountNumSatisfyingCriterion, self).process(num);
        if (self.criterion(num)):
            self.numSatisfying += 1;
    def finalise(self, **kwargs):
        self.val = self.numSatisfying;
        if (self.percentIncidence):
           self.val = float(self.val)/self.numExamplesSeen;      

class CountNonZeros(CountNumSatisfyingCriterion):
    def __init__(self, name, **kwargs):
        super(CountNonZeros, self).__init__(name, lambda x: x != 0, "NumNonZeros", **kwargs); 


