from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;

#Why can't I find an implementation of this?
class Node(object):
    def __init__(self,value,parent,nextVal=None,prevVal=None):
        self.value = value
        self.parent=parent;
        self.nextVal = nextVal
        self.prevVal = prevVal;
    def delete(self):
        if (self.parent.first==self):
            assert self.prevVal is None;
            self.parent.first = self.nextVal;
        else:
            self.prevVal.nextVal = self.nextVal; 
        if (self.parent.last==self):
            assert self.nextVal is None;
            self.parent.last=self.prevVal
    def deleteAllRemaining(self):
        print(self);
        self.nextVal = None;
        self.parent.last = self;
        print(self.parent.first)
        print(str(self.parent));
    def deleteAllPrevious(self):
        self.prevVal = None;
        self.parent.first = self;
    def __str__(self):
        return str(self.value)

class LinkedListIterator(object):
    def __init__(self, linkedList):
        self.linkedList = linkedList;
        self.curr = None;
    def next(self):
        if (self.curr is None) and (self.linkedList.first is not None):
            self.curr = self.linkedList.first
            return self.curr
        elif (self.curr is not None) and self.curr.nextVal is not None:
            self.curr = self.curr.nextVal
            return self.curr
        else:
            raise StopIteration

#Why can't I find an implementation of this?
class LinkedList(object):
    def __init__(self):
        self.first = None
        self.last = None
        self.curr = None;
    def append(self, x):
        toAdd = Node(value=x, parent=self, nextVal=None, prevVal=self.last);
        if (self.last is None): #there was nothing in the list
            assert self.last==self.first;
            self.first = toAdd;
        else:
            self.last.nextVal=toAdd;
        self.last=toAdd;
    def __iter__(self):
        return LinkedListIterator(self);
    def __str__(self):
        return str([str(x) for x in self]);
