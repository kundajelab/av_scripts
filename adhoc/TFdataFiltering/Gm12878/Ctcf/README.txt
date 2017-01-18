ln -s /mnt/data/ENCODE/peaks_spp/mar2012/distinct/idrOptimalBlackListFilt/wgEncodeBroadHistoneGm12878CtcfStdAlnRep0.bam_VS_wgEncodeBroadHistoneGm12878ControlStdAlnRep0.bam.regionPeak.gz idrChipSeqPeaks.gz
scp avanti@vayu.stanford.edu:/srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/RelaxedPeaks/wgEncodeBroadHis*Gm12878Ctcf* relaxedChipSeqPeaks.gz

./processData.sh
