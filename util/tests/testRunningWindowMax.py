import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;
import numpy as np;

class TestRunningWindowMax(unittest.TestCase):
    def testRunningWindowMax1(self):
        self.assertListEqual(
            list(util.computeRunningWindowMax(np.array([1,2,3,4,5,6]),3))
            ,[3,4,5,6]);
    def testRunningWindowMax2(self):
        self.assertListEqual(
            list(util.computeRunningWindowMax(np.array([6,5,4,3,2,1]),3))
            ,[6,5,4,3]);
    def testRunningWindowMax3(self):
        self.assertListEqual(
            list(util.computeRunningWindowMax(np.array([1,2,3,2,1,0]),3))
            ,[3,3,3,2]);
