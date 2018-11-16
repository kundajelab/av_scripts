ln -s /mnt/data/ENCODE/peaks_spp/mar2012/distinct/idrOptimalBlackListFilt/wgEncodeHaibTfbsGm12878Pu1Pcr1xAlnRep0.bam_VS_wgEncodeHaibTfbsGm12878RxlchPcr1xAlnRep0.bam.regionPeak.gz idrChipSeqPeaks.gz
scp avanti@vayu.stanford.edu:/srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/RelaxedPeaks/wgEncode*Gm12878*Pu1* relaxedChipSeqPeaks.gz

./processData.sh
