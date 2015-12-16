#produces kmerIds_k-3_testFasta.txt.gz, which has the fasta sequence represented using ids representing the kmers
./fastaToKmerIndices.py --fastaInput testFasta.fa --kmerLength 3

#produces kmerCountsPerSeq_kmerIds_k-3_testFasta.txt.gz, which has the actual kmer counts
./computeKmerCounts.py --inputFile kmerIds_k-3_testFasta.txt.gz --kmerLength 3

#produces revComp_kmerCountsPerSeq_kmerIds_k-3_testFasta.txt.gz which adds in reverse complemented kmer counts
./reverseComplementKmerCounts.py --inputFile kmerCountsPerSeq_kmerIds_k-3_testFasta.txt.gz
