#!/usr/bin/env sh

perl -le 'print "id\tlabel"' > labels.txt
zcat centered_800bp_idrChipSeqPeaks.gz | perl -lane 'print "$F[0]:$F[1]-$F[2]\t1"' >> labels.txt 
zcat centered_800bp_filteredDNase_top150000_relaxedPeaks.gz | perl -lane 'print "$F[0]:$F[1]-$F[2]\t0"' >> labels.txt
