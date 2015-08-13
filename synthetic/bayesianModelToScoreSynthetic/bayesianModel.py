from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import fileProcessing as fp;
import util;
from collections import namedtuple;
from pwm import pwm;
import numpy as np;

#strategy when there are multiple grammars per sequence:
# - iterate over number of possible grammars
# greedily select the top pairs of positions for grammars (or maybe some non-greedy search)?
# --> score the background given those positions picked...
# -> run with the single combo that gives the best results...


class CacheForSingleSequence(object):
    def __init__(self, seq, motifNameToMotifScoreTrack,background=util.DEFAULT_BACKGROUND_FREQ):
        self.seq = seq;
        self.motifNameToMotifScoreTrack; #positions in motifScoreTrack should indicate start positions of motifs.
        self.scoreSeqAccordingToBackground(background); #get the log prob at each position
    def scoreSeqAccordingToBackground(background):
        """
            background is of formate Letter: prob
        """
        self.backgroundLogProbTrack = [];
        self.totalBackgroundLogProb = 0;
        for letter in seq:
            self.backgroundScoreTrack.append(np.log(background[letter]));
            self.totalBackgroundLogProb += self.backgroundLogProbTrack[-1];
    def getPseqGivenGrammar(self, seq, grammar):
        """
            Computes P(seq|grammar)
            seqName: an id for the seq to be used to access the cache
            seq: the actual sequence of bases to compute P(seq|grammar) on
            grammar: an instance of AbstractGrammar. Has all the info on the grammar
        """
        PseqGivenGrammar = 0; #initialise to 0 then sum over all spacings/positions
        #iterate over all possible spacings between the motif, and the
        #corresponding probability of that spacing (for the grammars where all spacings
        #are uniformly probable, probabilityOfSpacing will be fixed)
        for (spacing, probabilityOfSpacing) in grammar.getPossibleSpacingsAndTheirProbabilities():
            #compute the total length of the grammar, which is the size of the spacing plus the motifs
            totalGrammarLength = spacing + grammar.motif1.pwmSize + grammar.motif2.pwmSize;
            #if the grammar of this size would fit in the sequence...
            if (totalGrammarLength < len(seq)):
                #since the start positions are sampled uniformly, compute the total number of
                #possible start positions for a grammar of this size, and use
                #that to find the probability of each start position
                probabilityOfEachStartPos = float(1)/(len(seq)-totalGrammarLength+1);
                #iterate over all the possible start positions
                for startPos in xrange(0, len(seq)-totalGrammarLength):
                    #using the cache, get the probability that the sequence underlying the motifs in this particular
                    #combination of startPos and spacing originated from their corresponding PWMs
                    endPosOfMotif1 = startPos + grammar.motif1.pwmSize;
                    firstPosOfMotif2 = lastPosOfMotif1 + spacing;
                    endPosOfMotif2 = firstPosOfMotif2 + grammar.motif2.pwmSize;
                    motif1Prob = self.getProbForMotifAtPosition(seqName, grammar.motif1.name, startPos);
                    motif2Prob = self.getProbForMotifAtPosition(seqName, grammar.motif2.name, firstPosOfMotif2);
                    #using the cache, get the probability that all sites that aren't occupied by motifs
                    #originated from the background model
                    backgroundPositionsToExclude = range(startPos, endPosOfMotif1) + range(firstPosOfMotif2,endPosOfMotif2);                    
                    backgroundPositionsProb = self.getProbForBackgroundAtAllPositionsExcept(seqName, backgroundPositionsToExclude);
                    #P(seq|grammar) += P(spacing|grammar)*P(startPos|spacing)
                                        #*P(motif1|motif1location)
                                        #*P(motif2|motif2location)
                                        #*P(seqEverywhereExceptMotif1andMotif2|background)
                    PseqGivenGrammar += probabilityOfSpacing*probabilityOfEachStartPos*motif1Prob*motif2Prob*backgroundPositionsProb;
        return PseqGivenGrammar; 
    def getProbForBackgroundAtAllPositionsExcept(self, seqName, arrayOfPositionsToExclude):
        totalLogProbToSubstract = 0;
        for pos in arrayOfPositionsToExclude:
            totalLogProbToSubstract += self.backgroundLogProbTrack[pos]
        return self.totalBackgroundLogProb - totalLogProbToSubstract;
    def getProbForMotifAtPosition(self, seqName, motifName, position):
        return self.motifNameToMotifScoreTrack[motifName][position];

class AbstractGrammar(object):
    def __init__(self, motif1, motif2):
        """
            motif1 and motif2 are instances of pwm.PWM
        """
        self.motif1 = motif1;
        self.motif2 = motif2;
    def getPossibleSpacingsAndTheirProbabilities(self):
        """
            return an array of tuples, consisting of the spacing
                and the probability of that spacing
        """
        raise NotImplementedError();

class UniformVariableSpacingGrammar(Grammar):
    def __init__(self, motif1, motif2, minSpacing, maxSpacing):
        """
            maxSpacing and minSpacing are inclusive
        """
        super(UniformVariableSpacingGrammar, self).__init__(motif1, motif2);
        self.minSpacing = minSpacing;
        self.maxSpacing = maxSpacing;
    def getPossibleSpacingsAndTheirProbabilities(self):
        probability = float(1)/(maxSpacing-minSpacing+1); 
        return [(x, probability) for x in xrange(self.minSpacing, self.maxSpacing+1)];

