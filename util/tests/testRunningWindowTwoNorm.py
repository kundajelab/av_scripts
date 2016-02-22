import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;
import numpy as np;

class TestRunningWindowTwoNorm(unittest.TestCase):
    def testRunningWindowTwoNorm1(self):
        self.assertListEqual(
            list(util.computeRunningWindowTwoNorm(np.array([1,2,3,4,5,6]),3))
            ,[np.linalg.norm([1,2,3])
                ,np.linalg.norm([2,3,4])
                ,np.linalg.norm([3,4,5])
                ,np.linalg.norm([4,5,6])]);
