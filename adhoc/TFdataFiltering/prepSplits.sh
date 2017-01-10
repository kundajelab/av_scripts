#!/usr/bin/env bash
splits="splits"
mkdir $splits
labels="labels.gz"
zcat $labels | egrep -w -v 'chr1|chr2|id' | perl -lape '$_ = $F[0]' | gzip -c > $splits/"train.gz" 
zcat $labels | egrep -w 'chr1' | perl -lape '$_ = $F[0]' | gzip -c > $splits/"valid.gz" 
zcat $labels | egrep -w 'chr2' | perl -lape '$_ = $F[0]' | gzip -c > $splits/"test.gz" 

