#!/usr/bin/env bash

echo "cutting the head off the labels"
cat unshuffled_labels.txt | perl -lane 'if ($. > 1) {print $_}' | gzip -c > headless_unshuffled_labels.txt.gz

#shuffle
echo "shuffling"
shuffle_corresponding_lines headless_unshuffled_labels.txt.gz
echo "done shuffling"

echo "extracting fasta"
bedtools getfasta -fi /mnt/data/annotations/by_organism/human/hg19.GRCh37/hg19.genome.fa -bed headless_unshuffled_labels.txt.gz -tab -fo shuffled_features.fa

echo "gzipping fasta"
gzip shuffled_features.fa

echo "making a labels file that has the title"
head -1 unshuffled_labels.txt | gzip -c > shuffled_labels.txt.gz 
zcat shuffled_headless_unshuffled_labels.txt.gz | gzip -c >> shuffled_labels.txt.gz
rm shuffled_headless_unshuffled_labels.txt.gz
rm headless_unshuffled_labels.txt.gz

#before, when I tried to shuffle the fasta directly
#echo "concatenating fasta into a single file"
#zcat features_unshuffled.fa.gz | perl -lane 'BEGIN {$title=undef} {if ($.%2==1) {$title=$_} else {print $title."|".$_}}' | gzip -c > unshuffled_concatenated_features.fa.gz
#echo "shuffling"
#shuffle_corresponding_lines headless_unshuffled_labels.txt.gz unshuffled_concatenated_features.fa.gz
#echo "getting back the fasta from the shuffled lines"
#zcat shuffled_unshuffled_concatenated_features.fa.gz | perl -lane '($id, $seq) = split(/\|/, $_); print($id); print($seq)' | gzip -c > shuffled_inputs.fa.gz
#rm unshuffled_concatenated_features.fa.gz
#rm shuffled_unshuffled_concatenated_features.fa.gz

