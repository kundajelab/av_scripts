
#assuming the distributions we are finding stats
#for are one-dimensional, for now.
def IterativeStatsFinder(object):
    """
        Abstract class. Pass in values with .process(num)
        and then call finalise(self, **kwargs) when done
    """
    def __init__(self, name):
        self.name = name;
        self.numExamplesSeen = 0;
    def process(self, num):
        self.numExamplesSeen += num;
    def finalise(self, **kwargs):
        raise NotImplementedError();
    def getVal(self):
        if hasattr(self, 'val') == False:
            raise "No attribute val; have you called finalise?";
        return self.val;
    def getFinderType():
        if hasattr(self, 'finderType') == False:
            raise "FinderType not defined for this class";
        return self.finderType;

def MeanFinder(IterativeStatsFinder):
    self.finderType="Mean";
    def __init__(self, name):
        super(MeanFinder, self).__init__(self, name);
        self.total = 0;
    def process(self, num):
        super(MeanFinder, self).process(self, num);
        self.total += 1;
    def finalise(self, **kwargs):
        self.val = float(self.total)/self.numExamplesSeen;

def VarianceFinder(IterativeStatsFinder):
    self.finderType="Variance";
    def __init__(self, name):
        super(VarianceFinder, self).__init__(self, name);
        self.meanFinder = MeanFinder(name+"_meanFinder");
        self.meanSquareFinder = MeanFinder(name+"_meanSquareFinder");
        self.squaredTotal = 0;
    def process(self, num):
        super(VarianceFinder, self).process(self, num);
        self.meanFinder.process(num);
        self.meanSquareFinder.process(num**2);
    def finalise(self, **kwargs):
        self.meanFinder.finalise();
        self.meanSquareFinder.finalise();
        self.val = float(self.meanSquareFinder.getVal() - (self.meanFinder.getVal()**2));

def SdevFinder(IterativeStatsFinder):
    self.finderType = "StandardDeviation"
    def __init__(self, name):
        super(SdevFinder, self).__init__(self, name);
        self.varianceFinder = VarianceFinder(name+"_varianceFinder");
    def process(self, num):
        super(VarianceFinder, self).process(self, num);
        self.varianceFinder.process(num);
    def finalise(self, **kwargs):
        self.varianceFinder.finalise();
        self.val = self.varianceFinder.getVal()**(0.5);

def CountNumSatisfyingCriterion(IterativeStatsFinder):
    def __init__(self, name, criterion, finderType):
        """
            criterion is a function that takes as argument 'num'
        """
        super(CountNumGreaterThanOrEqualTo, self).__init__(self, name);
        self.criterion = criterion;
        self.numSatisfying = 0;
        self.finderType = finderType;
    def process(self, num):
        if (criterion(num)):
            self.numSatisfying += 1;
    def finalise(self, **kwargs):
       self.val = self.numSatisfying;         

def CountNonZeros(CountNumSatisfyingCriterion):
    def __init__(self, name):
        super(CountNonZeros, self).__init__(self, name, lambda x: x != 0, "NumNonZeros"); 


