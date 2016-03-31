from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import unittest;
from unittest import skip;

class TestRavel(unittest.TestCase):
    def testRavel(self):
        self.assertListEqual([1,2,3,4],util.unravelIterable([1,[[2]], [3,4]])) 
