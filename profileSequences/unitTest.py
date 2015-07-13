import profileSequences;
from profileSequences import getKmerGenerator;
kmerGenerator = getKmerGenerator(None, 4, False);
print [x for x in kmerGenerator("ACGNTCcgTAATTTGATAGnGGGGTGCCCC")];
