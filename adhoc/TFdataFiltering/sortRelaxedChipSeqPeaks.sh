#!/usr/bin/env bash
#shoul be run in a folder where relaxedChipSeqPeaks.gz has been symlinked to the appropriate file
zcat relaxedChipSeqPeaks.gz | sort --key 7rn,7rn > sorted_relaxedChipSeqPeaks
gzip -f sorted_relaxedChipSeqPeaks
