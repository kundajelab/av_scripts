#IDR peaks
ln -s /srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/idrOptimalBlackListFilt/wgEncodeHaibTfbsH1hescNanogsc33759V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz idChipSeqPeaks.gz
#Relaxed peaks
ln -s /srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/RelaxedPeaks/wgEncodeHaibTfbsH1hescNanogsc33759V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz relaxedChipSeqPeaks.gz

#On nandi: /users/avanti/scratch/Pou5f1_Nanog/Nanog/
based on avanti@vayu.stanford.edu:/home/avanti/mainDir/adhoc_Pou_Nanog_H1ESC/
processing scripts are in: av_scripts/adhoc/TFdataFiltering/adhoc_Pou_Nanog_H1ESC/

ln -s fastaExtracted_centered_800bp_idrChipSeqPeaks.fa.gz positives.gz
ln -s fastaExtracted_centered_800bp_filteredDNase_top150000_relaxedPeaks.fa.gz negatives.gz
ln -s /users/avanti//av_scripts/importDataPackage/cannedYamls/fullYamlSets/basicPosNegFasta_categoricalLables yaml

{
 "seed": 1234
 ,"inputLen": 800
 ,"finalLayerActivation": "sigmoid"
 ,"numOutputs": 1
 ,"convLayers_numFilters": [30]
 ,"convLayers_kernelWidths": [45]
 ,"maxPool_width": 50
 ,"maxPool_stride_width": 20
 ,"optimizerType": "adam"
}


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
  --jsonDbFile runsDb.rb

