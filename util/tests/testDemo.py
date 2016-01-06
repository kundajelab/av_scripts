import unittest;
from unittest import skip;

class TestSetupAndTeardown(unittest.TestCase): 
    def setUp(self):
        self.myHappyList = [1,2,3]

    def testSetup1HappyName(self):
        self.myHappyList[0] = 2;
        self.assertListEqual(self.myHappyList, [2,2,3])

    def testSetup2(self):
        self.myHappyList[1] = 3;
        self.assertListEqual(self.myHappyList, [1,3,3])

class TestBasic(unittest.TestCase):
    def testBasic(self):
        self.assertEqual(1,1) 
   
    @skip 
    def testBasic(self):
        self.assertEqual(1,2) 

    @skip 
    def testDemo(self):
        self.assertListEqual([1,2,3],[1,2,4]);
    
    def testError(self):
        with self.assertRaises(IndexError) as context:
            "abcd"[5];
    
    def testAlmostEqual(self):
        self.assertAlmostEqual(0.11,0.12,places=1);

    def testNotAlmostEqual(self):
        self.assertNotAlmostEqual(0.11,0.12,places=2);
