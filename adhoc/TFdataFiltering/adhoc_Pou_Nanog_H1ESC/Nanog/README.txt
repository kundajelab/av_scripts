#IDR peaks
ln -s /srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/idrOptimalBlackListFilt/wgEncodeHaibTfbsH1hescNanogsc33759V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz idChipSeqPeaks.gz
#Relaxed peaks
ln -s /srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/RelaxedPeaks/wgEncodeHaibTfbsH1hescNanogsc33759V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz relaxedChipSeqPeaks.gz

#On nandi: /users/avanti/scratch/Pou5f1_Nanog/Nanog/
based on avanti@vayu.stanford.edu:/home/avanti/mainDir/adhoc_Pou_Nanog_H1ESC/
processing scripts are in: av_scripts/adhoc/TFdataFiltering/adhoc_Pou_Nanog_H1ESC/

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

