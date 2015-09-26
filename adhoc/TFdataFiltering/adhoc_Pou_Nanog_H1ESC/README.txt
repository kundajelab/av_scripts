#positive: 800 bp centered on the TF chip seq summits
#Negative: 
#--> Sort col 7 from HIGH to LOW, take top 100k
#--> filter out any DNAse peaks in cell type that overlap them by even 1bp
#--> use 800bp centered around summit (LAST COLUMN) as negative set.

ln -s /mnt/data/epigenomeRoadmap/peaks/consolidated/narrowPeak/E003-DNase.macs2.narrowPeak.gz cellTypeDNasePeaks.gz
