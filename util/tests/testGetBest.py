import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;

class TestGetBest(unittest.TestCase):

    def testGetMax(self):
        self.assertTupleEqual(
            util.getBest(["1","2","1"]
                        ,getterFunc=int
                        ,takeMax=True)
            ,("2",2)
        );  

    def testGetMin(self):
        self.assertTupleEqual(
            util.getBest(["1","0","1"]
                        ,getterFunc=int
                        ,takeMax=False)
            ,("0",0)
        );  

    def testTie(self):
        self.assertTupleEqual(
            util.getBest(enumerate(["1","0","1"])
                        ,getterFunc=lambda x: int(x[1])
                        ,takeMax=True)
            ,((0,"1"),1)
        );  


