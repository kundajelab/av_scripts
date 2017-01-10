#!/usr/bin/env bash
#Should be run in a subfolder where all the necessary input files have been symlinked
#Expects sortRelaxedChipSeqPeaks.sh to have been run

SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ="sorted_relaxedChipSeqPeaks" #file has gz suffix. sorted by 7th column in descending order.
CELL_TYPE_DNASE_PEAKS="../cellTypeDNasePeaks.gz"
TOPN=150000 #will only consider this many of the sorted, relaxed chipseq peaks, since they are SUPER relaxed
WINDOW=1000

SORTED_RELAXED_CHIPSEQ_PEAKS=${SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ}".gz"
TOPN_SORTED_PEAKS_FILENAME_NOGZ="top"${TOPN}"_"${SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ}

zcat $SORTED_RELAXED_CHIPSEQ_PEAKS | head -${TOPN} > $TOPN_SORTED_PEAKS_FILENAME_NOGZ
gzip -f $TOPN_SORTED_PEAKS_FILENAME_NOGZ
TOPN_SORTED_PEAKS_FILENAME=${TOPN_SORTED_PEAKS_FILENAME_NOGZ}".gz"

OUTPUT_FILE="filteredDNase_top"${TOPN}"_relaxedPeaks"
CENTERED_OUTPUT_FILE="centered_"${WINDOW}"bp_"${OUTPUT_FILE}

bedtools intersect -v -wa -a ${CELL_TYPE_DNASE_PEAKS} -b ${TOPN_SORTED_PEAKS_FILENAME} > $OUTPUT_FILE
gzip -f $OUTPUT_FILE

#executables below live in av_scripts/exec
recenterSequences.py --outputFile $CENTERED_OUTPUT_FILE".gz" --sequencesLength $WINDOW --chromSizesFile ../hg19_chromsizes.txt ${OUTPUT_FILE}".gz" --summitOffsetColIndex 9
bedToFasta.py --inputBedFile centered_${WINDOW}bp_filteredDNase_top${TOPN}_relaxedPeaks.gz --faPath /mnt/data/annotations/by_organism/human/hg19.GRCh37/hg19.genome.fa
