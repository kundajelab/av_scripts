from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;

def identifyPeaks(arr):
    #use a state machine to identify peaks
    #"peaks" as defined by larger than neighbours
    #for tied region, take the middle of the tie.
    #return tuples of idx + peak val
    previousVal = None
    foundPeaks = [];
    for idx, val in enumerate(arr):
        if (previousVal is not None):
            if (val > previousVal):
                potentialPeakStartIdx = idx;
            elif (val < previousVal):
                if (potentialPeakStartIdx is not None):
                    #peak found!
                    foundPeaks.append((int(0.5*(potentialPeakStartIdx+(idx-1))), previousVal));
                potentialPeakStartIdx = None;
                potentialPeakStartVal = None;
            else:
                #tie...don't change anything.
                pass;
        previousVal = val;
    return foundPeaks;
 
            
         
                
             
         
