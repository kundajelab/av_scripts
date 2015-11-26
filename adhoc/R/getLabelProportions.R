tab <- read.table("/mnt/lab_data/kundaje/users/pgreens/projects/hematopoiesis/data/atac_seq/merged_matrices/Leuk_35M_overlap_per_peak_merged_macsqval5_extended_top100000_bypval_labelled.txt.gz", header=TRUE, as.is=TRUE, comment.char="%") #fake comment char so it does not ignore the header
for (colName in names(tab)) {
    if (colName != "X.chr" && colName != "start" && colName != "end" && colName != "peak") {
        print(paste(colName,sum(tab[,colName])/100000))
    }
}
