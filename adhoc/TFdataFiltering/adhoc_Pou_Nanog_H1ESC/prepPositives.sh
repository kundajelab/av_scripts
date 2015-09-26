#!/usr/bin/env bash
#You should run this script in a folder that has the appropriate narrowpeak file linked
#as a symlink with the name idrChipSeqPeaks
RAW_POS_FILE_CORE="idrChipSeqPeaks" #assumed to be a gzipped file with .gz suffix
WINDOW=400 #+/- WINDOW around the summit
OUTPUT_POS_FILE="centered_halfWindow"${WINDOW}"_"${RAW_POS_FILE_CORE}
#The last column represents the offset from the summit

../centerAroundSummit.sh ${RAW_POS_FILE_CORE}".gz" $WINDOW $OUTPUT_POS_FILE
