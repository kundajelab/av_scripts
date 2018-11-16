#!/usr/bin/env bash

##simdata generation - install simdna
densityMotifSimulation.py --prefix ctcf --motifNames CTCF_known1 --max-motifs 2 --min-motifs 1 --mean-motifs 2 --seqLength 1000 --numSeqs 100 --rc-prob 0.5
emptyBackground.py --seqLength 1000 --numSeqs 1000 

#cleanup the _info files
rm *_info.txt

#zip things up
gzip -f *.simdata
gzip -f *.fa

###
#make the labels file without a title, to be shuffled
zcat DensityEmbedding_prefix-ctcf_motifs-CTCF_known1_min-1_max-2_mean-2_zeroProb-0_seqLength-1000_numSeqs-100.simdata.gz | perl -lane 'if ($. > 1) {print "$F[0]\t1"}' > labels_without_title.txt
zcat EmptyBackground_seqLength-1000_numSeqs-1000.simdata.gz | perl -lane 'if ($. > 1) {print "$F[0]\t0"}' >> labels_without_title.txt

#concatenate the fasta files to be one per line
zcat DensityEmbedding_prefix-ctcf_*.fa.gz EmptyBackground_*.fa.gz | perl -lane 'BEGIN {$title=undef} {if ($.%2==1) {$title=$_} else {print $title."|".$_}}' | gzip -c > concatenated_single_line_inputs.gz

#shuffle the lines
shuffle_corresponding_lines labels_without_title.txt concatenated_single_line_inputs.gz

#make the final inputs labels files from the shuffled lines
echo $'id\tctcf' > labels.txt
cat shuffled_labels_without_title.txt >> labels.txt
gzip -f labels.txt
zcat shuffled_concatenated_single_line_inputs.gz | perl -lane '($id, $seq) = split(/\|/, $_); print($id); print($seq)' | gzip -c > inputs.fa.gz
./data_aug_via_revcomp.sh
mv rc_aug_labels.txt.gz labels.txt.gz
mv rc_aug_inputs.fa.gz inputs.fa.gz

#remove the intermediate files
rm shuffled_labels_without_title.txt
rm labels_without_title.txt
rm concatenated_single_line_inputs.gz
rm shuffled_concatenated_single_line_inputs.gz
rm DensityEmbedding*.fa.gz
rm EmptyBackground*.fa.gz

mkdir splits
#make the splits
zcat labels.txt.gz | perl -lane 'if ($.%10 !=1 and $.%10 != 2) {print $F[0]}' | gzip -c > splits/train.txt.gz
zcat labels.txt.gz | perl -lane 'if ($.%10==1 and $. > 1) {print $F[0]}' | gzip -c > splits/valid.txt.gz
zcat labels.txt.gz | perl -lane 'if ($.%10==2) {print $F[0]}' | gzip -c > splits/test.txt.gz

make_hdf5 --yaml_configs make_hdf5_yaml/* --output_dir .
