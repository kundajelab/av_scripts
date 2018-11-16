#!/usr/bin/env bash
#You should run this script in a folder that has the appropriate narrowpeak file linked
#as a symlink with the name idrChipSeqPeaks
RAW_POS_FILE_CORE="idrChipSeqPeaks" #assumed to be a gzipped file with .gz suffix
WINDOW=1000
OUTPUT_POS_FILE="centered_"${WINDOW}"bp_"${RAW_POS_FILE_CORE}
#The last column represents the offset from the summit

#executables below live in av_scripts/exec
recenterSequences.py --outputFile $OUTPUT_POS_FILE".gz" --sequencesLength $WINDOW --chromSizesFile ../hg19_chromsizes.txt ${RAW_POS_FILE_CORE}".gz" --summitOffsetColIndex 9

#add shifts
zcat "centered_"${WINDOW}"bp_idrChipSeqPeaks.gz" | perl -lane 'print("$F[0]\t$F[1]\t$F[2]\t$F[3]\t$F[4]"); foreach $i(1..25) {$shift=-$i*2; $start = $F[1]-$shift; $end = $F[2]-$shift; print $F[0]."\t$start\t$end\t$F[3]\tshift$shift:$F[0]:$start"."-".$end; $shift=$i*2; $start = $F[1]+$shift; $end = $F[2]+$shift; print $F[0]."\t$start\t$end\t$F[3]\tshift+$shift:$F[0]:$start"."-".$end}' | gzip -c > "shifts_added_centered_"${WINDOW}"bp_idrChipSeqPeaks.gz"
