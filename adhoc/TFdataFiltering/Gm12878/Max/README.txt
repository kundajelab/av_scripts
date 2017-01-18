ln -s /mnt/data/ENCODE/peaks_spp/mar2012/distinct/idrOptimalBlackListFilt/wgEncodeSydhTfbsGm12878MaxIggmusAlnRep0*.gz idrChipSeqPeaks.gz
scp avanti@vayu.stanford.edu:/srv/scratch/jisraeli/TF_Binding/Data/MultiCellType/RelaxedPeaks/wgEncode*Gm12878*MaxIggmus* relaxedChipSeqPeaks.gz

./processData.sh
