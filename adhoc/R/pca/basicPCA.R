inputFile="input.txt"
outputFile="output.txt"
dat <- read.table(inputFile, header=TRUE, as.is=TRUE, row.names=1)
components = prcomp(dat)

#DO NOT FORGET THAT THERE IS NO BEGINNING TAB
write.table(components$x, outputFile, col.names=TRUE, row.names=TRUE, quote=FALSE, sep="\t")

#plotting components against each other
lim=10
for (i in 1:lim) {
    for (j in 1:i) {
        if (i != j) {
            png(paste("pc",j,"vs",i,".png"));
            plot(components$x[,i], components$x[,j],ylab=paste("pc",j),xlab=paste("pc",i))
            dev.off();
        }
    }
}

