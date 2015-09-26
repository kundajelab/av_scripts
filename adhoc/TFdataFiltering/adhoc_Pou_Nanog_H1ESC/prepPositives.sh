#!/usr/bin/env bash
#You should run this script in a folder that has the appropriate narrowpeak file linked
#as a symlink with the name idrChipSeqPeaks
RAW_POS_FILE_CORE="idrChipSeqPeaks" #assumed to be a gzipped file with .gz suffix
WINDOW=800
OUTPUT_POS_FILE="centered_"${WINDOW}"bp_"${RAW_POS_FILE_CORE}
#The last column represents the offset from the summit

/scratch/avanti/av_scripts/exec/recenterSequences.py --outputFile $OUTPUT_POS_FILE".gz" --sequencesLength $WINDOW --chromSizesFile ../hg19_chromsizes.txt ${RAW_POS_FILE_CORE}".gz"
