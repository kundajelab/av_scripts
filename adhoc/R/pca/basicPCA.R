dat <- read.table("fftApplied_slidingWindow_n53_autoencoderModel_joined_featuresExtracted_seqLen2000_one_hot_test_jisraeliSplit_noN_titled_joined_4000bp_forJisraeli.tsv", header=TRUE, as.is=TRUE, row.names=1)
components = prcomp(dat)
