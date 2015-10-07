from seqToKmerIds import seqsToKmerIds;
from seqToKmerIds import getKmerOrdering;

testSeqs  = ['ACGTN', 'ACNGT']
print(seqsToKmerIds(testSeqs, 3));
print(getKmerOrdering(3))
