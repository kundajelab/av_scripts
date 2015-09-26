#You should run this script in a folder that has the appropriate narrowpeak file linked
#as a symlink with the name idrChipSeqPeaks
RAW_POS_FILE_CORE="idrChipSeqPeaks" #assumed to be a gzipped file with .gz suffix
WINDOW=400 #+/- WINDOW around the summit
OUTPUT_POS_FILE="centered_halfWindow"${WINDOW}"_"${RAW_POS_FILE_CORE}".bed"
#The last column represents the offset from the summit

zcat ${RAW_POS_FILE_CORE}".gz" | perl -lape '$chrom=$F[0]; $start=$F[1]; $end=$F[2]; $offset=$F[$#F]; $center=$start+$offset; $halfWindow='${WINDOW}'; $newStart=$center-$halfWindow; $newEnd=$center+$halfWindow; $_="$chrom\t$newStart\t$newEnd"' > $OUTPUT_POS_FILE
gzip $OUTPUT_POS_FILE
