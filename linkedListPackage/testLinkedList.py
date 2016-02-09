import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import linkedListPackage;
from linkedListPackage.linkedList import LinkedList;
import unittest;
from unittest import skip;

class TestLinkedList(unittest.TestCase):

    def stringify(self, arr):
        return str([str(x) for x in arr]);  

    def getBasicLinkedList(self):
        linkedList = LinkedList();  
        linkedList.append(1);
        linkedList.append(2);
        linkedList.append(3);
        return linkedList;

    def getTwoElementLinkedList(self):
        linkedList = LinkedList();  
        linkedList.append(1);
        linkedList.append(2);
        return linkedList;
        
    def getSingleElementLinkedList(self):
        linkedList = LinkedList();
        linkedList.append(1);
        return linkedList;
         
    def testLinkedList(self):
        linkedList = self.getBasicLinkedList();
        self.assertEqual(str(linkedList),self.stringify([1,2,3])); 

    def _testOpOnlyElement(self, op): 
        linkedList = self.getSingleElementLinkedList();
        iterator = iter(linkedList);
        first = iterator.next();
        op(first);
        return linkedList;

    def _testOpFirst(self, op):
        linkedList = self.getTwoElementLinkedList();
        iterator = iter(linkedList);
        first = iterator.next();
        op(first);
        return linkedList; 

    def _testOpLast(self, op):
        linkedList = self.getTwoElementLinkedList();
        iterator = iter(linkedList);
        iterator.next();
        last = iterator.next();
        op(last);
        return linkedList; 

    def _testOpMiddle(self, op):
        linkedList = self.getBasicLinkedList();
        iterator = iter(linkedList);
        iterator.next();
        middle = iterator.next();
        op(middle);
        return linkedList;

    def testDelete_onlyElement(self):
        linkedList = self._testOpOnlyElement(lambda x: x.delete());
        self.assertEqual(str(linkedList), self.stringify([])); 
        self.assertEqual(linkedList.first, None);
        self.assertEqual(linkedList.last, None);

    def testDeleteAllRemaining_onlyElement(self):
        linkedList = self._testOpOnlyElement(lambda x: x.deleteAllRemaining());
        self.assertEqual(str(linkedList), self.stringify([1])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 1);

    def testDeleteAllPrevious_onlyElement(self):
        linkedList = self._testOpOnlyElement(lambda x: x.deleteAllPrevious());
        self.assertEqual(str(linkedList), self.stringify([1])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 1);

    def testDelete_firstElement(self):
        linkedList = self._testOpFirst(lambda x: x.delete());
        self.assertEqual(str(linkedList), self.stringify([2])); 
        self.assertEqual(linkedList.first.value, 2);
        self.assertEqual(linkedList.last.value, 2);

    def testDeleteAllRemaining_firstElement(self):
        linkedList = self._testOpFirst(lambda x: x.deleteAllRemaining());
        self.assertEqual(str(linkedList), self.stringify([1])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 1);

    def testDeleteAllPrevious_firstElement(self):
        linkedList = self._testOpFirst(lambda x: x.deleteAllPrevious());
        self.assertEqual(str(linkedList), self.stringify([1,2])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 2);

    def testDelete_lastElement(self):
        linkedList = self._testOpLast(lambda x: x.delete());
        self.assertEqual(str(linkedList), self.stringify([1])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 1);

    def testDeleteAllRemaining_lastElement(self):
        linkedList = self._testOpLast(lambda x: x.deleteAllRemaining());
        self.assertEqual(str(linkedList), self.stringify([1,2])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 2);

    def testDeleteAllPrevious_lastElement(self):
        linkedList = self._testOpLast(lambda x: x.deleteAllPrevious());
        self.assertEqual(str(linkedList), self.stringify([2])); 
        self.assertEqual(linkedList.first.value, 2);
        self.assertEqual(linkedList.last.value, 2);

    def testDelete_middleElement(self):
        linkedList = self._testOpMiddle(lambda x: x.delete());
        self.assertEqual(str(linkedList), self.stringify([1,3])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 3);

    def testDeleteAllRemaining_middleElement(self):
        linkedList = self._testOpMiddle(lambda x: x.deleteAllRemaining());
        self.assertEqual(str(linkedList), self.stringify([1,2])); 
        self.assertEqual(linkedList.first.value, 1);
        self.assertEqual(linkedList.last.value, 2);

    def testDeleteAllPrevious_middleElement(self):
        linkedList = self._testOpMiddle(lambda x: x.deleteAllPrevious());
        self.assertEqual(str(linkedList), self.stringify([2,3])); 
        self.assertEqual(linkedList.first.value, 2);
        self.assertEqual(linkedList.last.value, 3);

