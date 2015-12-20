#!/usr/bin/env bash
splits="splits"
mkdir $splits
labels="labels.txt.gz"
zcat $labels | egrep -w -v 'chr1|chr2' | perl -lape '$_ = $F[0]' > $splits/"train.txt" 
zcat $labels | egrep -w 'chr1' | perl -lape '$_ = $F[0]' > $splits/"valid.txt" 
zcat $labels | egrep -w 'chr2' | perl -lape '$_ = $F[0]' > $splits/"test.txt" 

