#!/usr/bin/env bash
splits="splits"
mkdir $splits
labels="labels.txt"
cat $labels | egrep -w -v 'chr1|chr2|id' | perl -lape '$_ = $F[0]' > $splits/"train.txt" 
cat $labels | egrep -w 'chr1' | perl -lape '$_ = $F[0]' > $splits/"valid.txt" 
cat $labels | egrep -w 'chr2' | perl -lape '$_ = $F[0]' > $splits/"test.txt" 

