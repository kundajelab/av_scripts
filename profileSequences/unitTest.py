import profileSequences;
from profileSequences import getKmerCountsGenerator;
kmerCountsGenerator, kmersToCareAbout = getKmerCountsGenerator(None, 6);
print zip([x for x in kmerCountsGenerator("CCGTTTNAC")], kmersToCareAbout);
