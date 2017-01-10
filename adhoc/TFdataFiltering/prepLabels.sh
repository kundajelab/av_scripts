#!/usr/bin/env sh

pos_file="centered_1000bp_idrChipSeqPeaks.gz"
neg_file="centered_1000bp_filteredDNase_top150000_relaxedPeaks.gz"
zcat $pos_file | perl -lane 'print "$F[0]:$F[1]-$F[2]\t1"' | gzip -c > labels_tmp.gz 
zcat $neg_file | perl -lane 'print "$F[0]:$F[1]-$F[2]\t0"' | gzip -c >> labels_tmp.gz
zcat $pos_file $neg_file | gzip -c > all_input_coordinates.gz

#shuffle corresponding lines
#produces shuffled_all_input_coordinates.gz and shuffled_labels_tmp.gz
shuffle_corresponding_lines all_input_coordinates.gz labels_tmp.gz


perl -le 'print "id\tlabel"' | gzip -c > labels.gz
zcat shuffled_labels_tmp.gz | gzip -c >> labels.gz
rm labels_tmp.gz
rm all_input_coordinates.gz

