#CTCF case: sample from a motif, then label all motifs with a certain pair of A's as label1. CTCF presence gets a label2.

#Mix motifs case:
./mixtureOfMotifs.py --pathToMotifs motifs.txt --motifNames fake_AACGSSAA fake_AAGCSSAA --seqLength 50 --numSeqs 10000 --motifProb 0.5
./labelMotifs_presentOrNot.py mixMotifSim_motifs-fake_AACGSSAA+fake_AAGCSSAA_motifProb-0p5_seqLength-50_numSeqs-10000.simdata.gz
mv *mixMotifSim* ~/Research/Enhancer_Prediction/enhancer_prediction_code/featureSelector/deepLIFFT/benchmarking/IntraMotifDependence/GCorCG/
