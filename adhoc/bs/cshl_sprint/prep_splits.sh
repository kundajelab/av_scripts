#!/usr/bin/env bash
mkdir splits
zcat shuffled_labels.txt.gz | perl -lane 'if ($. > 1) {print $F[3]}' | egrep -w -v 'chr1|chr2|chr3|chr4' | gzip -c > splits/train.txt.gz
zcat shuffled_labels.txt.gz | perl -lane 'if ($. > 1) {print $F[3]}' | egrep -w 'chr1|chr2|chr3|chr4' | gzip -c > splits/other.txt.gz
