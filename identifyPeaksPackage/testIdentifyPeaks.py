import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import identifyPeaksPackage;
from identifyPeaksPackage.identifyPeaks import identifyPeaks;
import unittest;
from unittest import skip;

class TestIdentifyPeaks(unittest.TestCase):

    def testSinglePeakIdentification1(self):
        self.assertListEqual(
            identifyPeaks([1,2,1])
            ,[(1,2)]); 
    
    def testSinglePeakIdentification2(self):
        self.assertListEqual(
            identifyPeaks([1,2,1,0.5,1])
            ,[(1,2)]); 
    
    def testMultiplePeakIdentification(self):
        self.assertListEqual(
            identifyPeaks([1,2,1,0.5,1,1.5,1])
            ,[(1,2),(5,1.5)]); 

    def testTiedPeakIdentification(self):
        self.assertListEqual(
            identifyPeaks([None,None,1,2,2,1,0.5,1,1.5,1.5,1.5,1])
            ,[(3,2),(9,1.5)]); 
    
