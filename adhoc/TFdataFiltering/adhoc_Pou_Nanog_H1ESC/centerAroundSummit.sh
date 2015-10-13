#!/usr/bin/env bash
INPUT=$1 #assumed to be a gzipped narrowpeak file
WINDOW=$2
OUTPUT=$3 #should not have the gz suffix; will be gzipped

zcat ${INPUT} | perl -lape '$chrom=$F[0]; $start=$F[1]; $end=$F[2]; $offset=$F[$#F]; $center=$start+$offset; $halfWindow='${WINDOW}'; $newStart=$center-$halfWindow; $newEnd=$center+$halfWindow; $_="$chrom\t$newStart\t$newEnd"' > $OUTPUT
gzip $OUTPUT
