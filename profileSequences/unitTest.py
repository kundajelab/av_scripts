import profileSequences;
from profileSequences import getKmerCountsGenerator;
kmerCountsGenerator, kmersToCareAbout = getKmerCountsGenerator(None, 2);
print zip([x for x in kmerCountsGenerator("CCGT")], kmersToCareAbout);
