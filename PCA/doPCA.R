#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)
inputFile <- args[1]
outputFile <- args[2]
print(paste("inputFile",inputFile))
print(paste("outputFile",outputFile))
print("Do not forget to fix the title column of the resulting file!")
dat <- read.table(inputFile, header=TRUE, as.is=TRUE, row.names=1)
components = prcomp(dat)

#DO NOT FORGET THAT THERE IS NO BEGINNING TAB
write.table(components$x, outputFile, col.names=TRUE, row.names=TRUE, quote=FALSE, sep="\t")
