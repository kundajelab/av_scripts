#!/usr/bin/env bash
bedToFasta.py --inputBedFile shuffled_all_input_coordinates.gz --faPath /mnt/data/annotations/by_organism/human/hg19.GRCh37/hg19.genome.fa

../prepLabels.sh
../prepSplits.sh

ln -s fastaExtracted_shuffled_all_input_coordinates.fa.gz inputs.gz
ln -s /users/avanti/momma_dragonn/momma_dragonn/data_loaders/yaml_import/canned_yamls/basic_fasta yaml

