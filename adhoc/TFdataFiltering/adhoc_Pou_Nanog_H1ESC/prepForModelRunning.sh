#!/usr/bin/env bash
ln -s fastaExtracted_centered_800bp_idrChipSeqPeaks.fa.gz positives.gz
ln -s fastaExtracted_centered_800bp_filteredDNase_top150000_relaxedPeaks.fa.gz negatives.gz
ln -s /users/avanti//av_scripts/importDataPackage/cannedYamls/fullYamlSets/basicPosNegFasta_categoricalLables yaml

../prepLabels.sh
../prepSplits.sh
