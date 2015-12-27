import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;

class TestRunningWindowSum(unittest.TestCase):
    def testRunningWindowSum(self):
        self.assertListEqual(
            util.computeRunningWindowSum([1,2,3,4,5,6],3)
            ,[6, 9, 12, 15]);

