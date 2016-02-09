ln -s /mnt/data/ENCODE/peaks_spp/mar2012/distinct/idrOptimalBlackListFilt/wgEncodeHaibTfbsH1hescPou5f1sc9081V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz idrChipSeqPaks.gz
ln -s /mnt/data/ENCODE/peaks_spp/mar2012/distinct/combrep/regionPeak/wgEncodeHaibTfbsH1hescPou5f1sc9081V0416102AlnRep0.bam_VS_wgEncodeHaibTfbsH1hescRxlchPcr1xAlnRep0.bam.regionPeak.gz relaxedChipSeqPeaks.gz

#On nandi: /users/avanti/scratch/Pou5f1_Nanog/Pou5f1/
based on avanti@vayu.stanford.edu:/home/avanti/mainDir/adhoc_Pou_Nanog_H1ESC/Pou5f1

{
    "inputLen": 800,
    "seed": 1234,
    "numOutputs": 1,
    "finalLayerActivation": "sigmoid",
    "convLayers_kernelWidths": [45],
    "convLayers_numFilters": [30],
    "convLayers_wLRmult": [3],
    "maxPool_width": 50,
    "maxPool_stride_width": 20,
    "optimizerType": "adam"
}
