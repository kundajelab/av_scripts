#!/usr/bin/env bash

numSeq=$1

##simdata generation - install simdna
#NOTE THAT VALID AND TRAIN HAVE BEEN SWAPPED; TRAIN SET IS SMALL!
rm variableSpacingGrammarSimulation_*
variableSpacingGrammarSimulation.py --prefix broad --motifName1 GATA_disc1 --motifName2 TAL1_known1 --seqLength 200 --numSeq $numSeq --minSpacing 0 --meanSpacing 5 --maxSpacing 10
variableSpacingGrammarSimulation.py --prefix tight --motifName1 GATA_disc1 --motifName2 TAL1_known1 --seqLength 200 --numSeq $numSeq --minSpacing 0 --meanSpacing 1 --maxSpacing 5

#cleanup the _info files
rm *_info.txt

#zip things up
gzip -f *.simdata
gzip -f *.fa

###
#make the labels file without a title, to be shuffled
zcat variableSpacingGrammarSimulation_prefix-broad*.simdata.gz | perl -lane 'if ($. > 1) {print "$F[0]\t1"}' > labels_without_title.txt
zcat variableSpacingGrammarSimulation_prefix-tight*.simdata.gz | perl -lane 'if ($. > 1) {print "$F[0]\t0"}' >> labels_without_title.txt

#concatenate the fasta files to be one per line
zcat variableSpacingGrammarSimulation_*.fa.gz | perl -lane 'BEGIN {$title=undef} {if ($.%2==1) {$title=$_} else {print $title."|".$_}}' | gzip -c > concatenated_single_line_inputs.gz

#shuffle the lines
shuffle_corresponding_lines labels_without_title.txt concatenated_single_line_inputs.gz

#make the final inputs labels files from the shuffled lines
echo $'id\tpos' > labels.txt
cat shuffled_labels_without_title.txt >> labels.txt
gzip -f labels.txt
zcat shuffled_concatenated_single_line_inputs.gz | perl -lane '($id, $seq) = split(/\|/, $_); print($id); print($seq)' | gzip -c > inputs.fa.gz

#remove the intermediate files
rm shuffled_labels_without_title.txt
rm labels_without_title.txt
rm concatenated_single_line_inputs.gz
rm shuffled_concatenated_single_line_inputs.gz
rm variableSpacingGrammarSimulation_*.fa.gz

mkdir splits
#make the splits
zcat labels.txt.gz | perl -lane 'if ($.%10 !=1 and $.%10 != 2) {print $F[0]}' | gzip -c > splits/train.txt.gz
zcat labels.txt.gz | perl -lane 'if ($.%10==1 and $. > 1) {print $F[0]}' | gzip -c > splits/valid.txt.gz
zcat labels.txt.gz | perl -lane 'if ($.%10==2) {print $F[0]}' | gzip -c > splits/test.txt.gz

make_hdf5 --yaml_configs make_hdf5_yaml/* --output_dir .
