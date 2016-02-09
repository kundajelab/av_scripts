import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;
import numpy as np;

class TestCrossCorr(unittest.TestCase):
    def testCrossCorr1(self):
        arr1 = np.array([
                 [2,0,1,0,0.5]
                ,[0,4,0,2,0  ]]);
        arr2 = np.array([
                 [1,0,1]
                ,[0,2,0]])
        results1 = util.crossCorrelateArraysLengthwise(arr1,arr2
                ,normaliseFunc=util.CROSSC_NORMFUNC.none 
                ,normaliseByMaxAtEachPos=False);
        results2 = util.crossCorrelateArraysLengthwise(arr1,arr2
                ,normaliseFunc=util.CROSSC_NORMFUNC.none 
                ,normaliseByMaxAtEachPos=True);
        self.assertAlmostEqual(results1[0][2],11)
        self.assertAlmostEqual(results1[0][4],5.5)
        self.assertAlmostEqual(results2[0][2],2.75)
        self.assertAlmostEqual(results2[0][4],2.75)
