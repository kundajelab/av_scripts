#!/usr/bin/env bash

#intended for augmenting your data with reverse complementation
#assumes that inputs.gz and labels.gz live in previous directory
zcat ../inputs.gz | perl -ne 'if ($.%2==1) {chomp;print} else {print "|".uc($_)}' | perl -F"\|" -lane '{print $F[0]; print $F[1]; print $F[0]."_rc"; $F[1] =~ y/ACGT/TGCA/; $_ = reverse $F[1]; print}' | gzip -c > inputs.gz
zcat ../labels.gz | perl -lane 'if ($. == 1) {print $_} else {print $_; print ($F[0]."_rc\t".$F[1])}' | gzip -c > labels.gz
