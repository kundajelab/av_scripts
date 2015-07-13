import profileSequences;
from profileSequences import getKmerCountsGenerator;
kmerCountsGenerator, kmersToCareAbout = getKmerCountsGenerator(None, 2, ['A','C','G','T']);
print [x for x in kmerCountsGenerator("ACGTACGT")], kmersToCareAbout;
