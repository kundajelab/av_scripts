#!/usr/bin/env bash
./prepLabels.sh

bedToFasta.py --inputBedFile shuffled_all_input_coordinates.gz --faPath /mnt/data/annotations/by_organism/human/hg19.GRCh37/hg19.genome.fa

./prepSplits.sh

ln -s fastaExtracted_shuffled_all_input_coordinates.fa.gz inputs.gz

