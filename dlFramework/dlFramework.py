scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetters;
import util;
from util import overrides;

class Argument(object):
    def __init__(self, keyword, value):
        self.keyword = keyword;
        self.value = value;
    def augment(self, string):
        return string+" "+self.keyword+" "+str(value);

class CommandConstructor(object):
    def __init__(self, beginningOfCommand):
        self.beginningOfCommand = beginningOfCommand;
    def produceCommand(self, args):
        toReturn = "beginningOfCommand ";
        for arg in args:
            toReturn = arg.augment(toReturn);
        return toReturn;

EXECUTOR_ACTIONS = util.enum(nothing="nothing", terminate="terminate");
METRIC_NAMES = util.enum(
    train_objective="train_objective"
    ,valid_objective="valid_objective"
    ,test_objective="test_objective"
);
class JobInfo(object):
    """
        When a job is executed, returns this object.
    """
    def __init__(self):
        self.iterationToMetrics = {};
        self.latestIteration = None;
    def updateWithMetric(self, iteration, metric, value):
        if iteration not in self.iterationToMetrics:
            self.iterationToMetrics[iteration] = {};
        self.iterationToMetrics[iteration][metric] = value;
    def updatesForIterationFinished(self, iteration):
        """
            Call this function when all the metrics for a
            particular iteration have been received.
        """
        self.latestIteration = iteration;
    def actionForExecutor(self):
        """
            Returns an EXECUTOR_ACTION
        """
        raise NotImplementedError();
    def finaliseJobPerf(self):
        raise NotImplementedError();
    def getFinalJobPerf(self):
        raise NotImplementedError();

class EarlyStoppingJobInfo(JobInfo):
    def __init__(self, iterationsOfNoImprovement):
        self.iterationsOfNoImprovement; 

    @overrides(JobInfo)
    def updatesForIterationFinished(self, iteration):
        super(EarlyStoppingJobInfo, self).updatesForIterationFinished(iteration);
         





