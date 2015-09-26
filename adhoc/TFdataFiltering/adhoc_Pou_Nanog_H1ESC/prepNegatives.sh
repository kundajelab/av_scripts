#Should be run in a subfolder where all the necessary input files have been symlinked
#Expects sortRelaxedChipSeqPeaks.sh to have been run

SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ="sorted_relaxedChipSeqPeaks" #file has gz suffix. sorted by 7th column in descending order.
CELL_TYPE_DNASE_PEAKS="../cellTypeDNasePeaks.gz"
TOPN=150000 #will only consider this many of the sorted, relaxed chipseq peaks, since they are SUPER relaxed
WINDOW=400

SORTED_RELAXED_CHIPSEQ_PEAKS=${SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ}".gz"
TOPN_SORTED_PEAKS_FILENAME_NOGZ="top"${TOPN}"_"${SORTED_RELAXED_CHIPSEQ_PEAKS_NOGZ}

zcat $SORTED_RELAXED_CHIPSEQ_PEAKS | head -${TOPN} > $TOPN_SORTED_PEAKS_FILENAME_NOGZ
gzip $TOPN_SORTED_PEAKS_FILENAME_NOGZ
TOPN_SORTED_PEAKS_FILENAME=${TOPN_SORTED_PEAKS_FILENAME_NOGZ}".gz"

OUTPUT_FILE="filteredDNase_top"${TOPN}"_relaxedPeaks"
CENTERED_OUTPUT_FILE="centered_halfWindow"${WINDOW}"_"${OUTPUT_FILE}

bedtools intersect -v -wa -a ${SORTED_RELAXED_CHIPSEQ_PEAKS} -b ${TOPN_SORTED_PEAKS_FILENAME} > $OUTPUT_FILE
gzip $OUTPUT_FILE

../centerAroundSummit.sh $OUTPUT_FILE".gz" $WINDOW $CENTERED_OUTPUT_FILE
