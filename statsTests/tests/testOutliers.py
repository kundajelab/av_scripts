import unittest;
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR to point to av_scripts");
sys.path.insert(0,scriptsDir);
import statsTests.outliers;
import numpy as np;

class TestOutliers(unittest.TestCase):
    def testGetG_oneTailed_max(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 50];
        G = statsTests.outliers.getG_max_oneTailed(arr);
        self.assertAlmostEqual(np.round(G,4), 2.8003); #compare to G from R.
    def testGrubbs_sorted(self):
        arr = [1,2,3,4,5,6,7,8,9,50];
        numOutliers =\
            statsTests.outliers.grubbsTest_max_findOutliers_sortedArr(arr, 0.05); 
        self.assertEqual(numOutliers, 1); 
    def testGrubbs_unsorted1(self):
        #results based on R outlier package
        arr = [5,6,7,8,9,50,1,2,3,4];
        outlierIndices =\
            statsTests.outliers.grubbsTest_max_findOutliers_unsortedArr(arr, 0.05); 
        self.assertListEqual(outlierIndices, [5]);
    def testGrubbs_unsorted2(self):
        #results based on R outlier package
        arr = [5,6,7,8,9,15,1,2,3,4];
        outlierIndices =\
            statsTests.outliers.grubbsTest_max_findOutliers_unsortedArr(arr, 0.05); 
        self.assertListEqual(outlierIndices, [5]);
    def testGrubbs_unsorted3(self):
        #results based on R outlier package
        arr = [5,6,7,8,9,14,1,2,3,4];
        outlierIndices =\
            statsTests.outliers.grubbsTest_max_findOutliers_unsortedArr(arr, 0.05); 
        self.assertListEqual(outlierIndices, []);
    def testGrubbs_unsorted4(self):
        #results based on R outlier package
        arr = [5,6,7,8,9,14,1,2,3,4];
        outlierIndices =\
            statsTests.outliers.grubbsTest_max_findOutliers_unsortedArr(arr, 0.07138); 
        self.assertListEqual(outlierIndices, []);
    def testGrubbs_unsorted5(self):
        #results based on R outlier package
        arr = [5,6,7,8,9,14,1,2,3,4];
        outlierIndices =\
            statsTests.outliers.grubbsTest_max_findOutliers_unsortedArr(arr, 0.07140); 
        self.assertListEqual(outlierIndices, [5]);
        
        
