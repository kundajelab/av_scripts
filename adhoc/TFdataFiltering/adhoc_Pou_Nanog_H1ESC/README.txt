#positive: 800 bp centered on the TF chip seq summits
#Negative: 
#--> Sort col 7 from HIGH to LOW, take top 100k
#--> filter out any DNAse peaks in cell type that overlap them by even 1bp
#--> use 800bp centered around summit (LAST COLUMN) as negative set.

ln -s /mnt/data/epigenomeRoadmap/peaks/consolidated/narrowPeak/E003-DNase.macs2.narrowPeak.gz cellTypeDNasePeaks.gz
ln -s /mnt/data/annotations/by_organism/human/hg19.GRCh37/hg19.chrom.sizes hg19_chromsizes.txt

on nandi: /users/avanti/scratch/Pou5f1_Nanog
copied from avanti@vayu.stanford.edu:/home/avanti/mainDir/adhoc_Pou_Nanog_H1ESC/

in particular subfolder, link these scripts from the previous (this) folder and run them:
./prepPositives.sh
./sortRelaxedChipSeqPeaks.sh
./prepNegatives.sh
./prepForModelRunning.sh

runKerasModel_dbTrack.py\
  --modelCreationClass ConvForSequenceModelCreator\
  --batchSize 50\
  --classWeights 0-1 1-25\
  --yamlConfigs yaml/*\
  --predictAndEvalClass AccStats\
  --predictAndEvalArgs " --printMajorityClassDebug"\
  --stoppingCriterionClass EarlyStopping\
  --stoppingCriterionArgs " --epochsToWaitForImprovement 3"\
  --emails avanti@stanford.edu\
  --jsonDbFile runsDb.db

