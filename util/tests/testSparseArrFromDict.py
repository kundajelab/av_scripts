
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;

class TestSparseArrFromDictionary(unittest.TestCase):
    def testIterableFromDict(self):
        self.assertListEqual(
            [x for x in util.IterableFromDict(
                            theDict={0:'b', 1:'a', 3:'c'}
                            ,defaultVal='x'
                            ,totalLen=4)]
            ,['b','a','x','c']);
    def testIterator(self):
        self.assertListEqual(
            [x for x in util.SparseArrFromDict(
                            theDict={0:'b', 1:'a', 3:'c'}
                            ,defaultVal='x'
                            ,totalLen=4)]
            ,['b','a','x','c']);
    def testDefaultVal(self):
        self.assertEqual(util.SparseArrFromDict({},0,2)[0], 0);
    def testIndexing(self):
        self.assertEqual(util.SparseArrFromDict({1:'a'},'x',2)[1],'a');
    def testIndexError(self):
        with self.assertRaises(IndexError):
            util.SparseArrFromDict({},0,2)[2]

    
