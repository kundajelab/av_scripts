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


#read labels
labels <- read.table(labels, header=TRUE, row.names=1, as.is=TRUE)
#assuming binary, map to colours:
cols=unlist(lapply(labels$X1,function(x) if(x==1) "red" else "blue"))
#plotting components against each other with labels
lim=5
for (i in 1:lim) {
    for (j in 1:i) {
        if (i != j) {
            png(paste("pc",j,"vs",i,".png"));
            plot(components$x[,i], components$x[,j],ylab=paste("pc",j),xlab=paste("pc",i),col=cols)
            dev.off();
        }
    }
}

cols=unlist(lapply(labels$X1,function(x) if(x==1) "red" else "blue"))
#plotting components against each other with labels
lim=5
for (i in 1:lim) {
    lines1 <- density(components$x[,i][labels==1])
    lines2 <- density(components$x[,i][labels==0])
    png(paste("pc",i,"labelDensity",".png", sep=""))
    plot(lines1,col="red",xlim=c(min(lines1$x,lines2$x),max(lines1$x,lines2$x)), ylim=c(min(lines1$y,lines2$y),max(lines1$y,lines2$y)), xlab=paste("pc",i))
    lines(lines2,col="blue")
    dev.off()
}

