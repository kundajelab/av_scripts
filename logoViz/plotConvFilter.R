#!/usr/bin/env Rscript
library(grid)
pathPrefix = paste(Sys.getenv(x = "UTIL_SCRIPTS_DIR", unset = "", names = NA),"/logoViz",sep="")
stormoPathPrefix = paste(pathPrefix,"/stormo_code",sep="")
source(paste(stormoPathPrefix,"/letterA.R",sep=""))
source(paste(stormoPathPrefix,"/letterC.R",sep=""))
source(paste(stormoPathPrefix,"/letterG.R",sep=""))
source(paste(stormoPathPrefix,"/letterT.R",sep=""))
source(paste(stormoPathPrefix,"/addLetter.R",sep=""))

plotConvFilter <- function (fileWithMotif, outfile, bias) {
    motifMatrix = as.matrix(read.table(fileWithMotif))
    motifLength = dim(motifMatrix)[1]
    biasByMotifLength = bias/motifLength 
    biasToPlot=-bias #could choose to norm by motif length
    maximumHeight = max(biasToPlot,max(rowSums(motifMatrix*(motifMatrix>=0))))
    minimumHeight = min(biasToPlot,min(0,min(rowSums(motifMatrix*(motifMatrix<0)))))
    #make a png of the appropriate height
    widthPerAlphabet = 1
    letterOrdering = c("A","C","G","T")
    letters <- list(x = NULL, y = NULL, id = NULL, fill = NULL)
    
  	tics = rep(0, motifLength)
    png(file=outfile, width=50*motifLength, height=500, units="px")
    grid.newpage()
    fontsize=15
    margin=5
  	pvp=plotViewport(c(margin, margin, margin, margin), name = "vp_margins")
    pushViewport(pvp)
    max_x = motifLength*widthPerAlphabet;
  	pushViewport(dataViewport(seq(0,max_x,0.01), seq(minimumHeight*1.01,maximumHeight,(maximumHeight-minimumHeight)/10), name = "vp_data"))
    for (colIdx in 1:motifLength) {
        thisColumn = motifMatrix[colIdx,]
        totalPositiveLettersHeightSoFar=0
        totalNegativeLettersHeightSoFar=0
        for (letterIdx in 1:4) {
            theLetter = letterOrdering[letterIdx];
            letterHeight = thisColumn[letterIdx]
            letterStartX = widthPerAlphabet*(colIdx-1)
            if (letterHeight >= 0) {
                letterStartY = totalPositiveLettersHeightSoFar
                totalPositiveLettersHeightSoFar = totalPositiveLettersHeightSoFar + letterHeight
            } else {
                letterStartY = totalNegativeLettersHeightSoFar
                totalNegativeLettersHeightSoFar = totalNegativeLettersHeightSoFar + letterHeight
            }
            letters=addLetter(letters,theLetter, letterStartX, letterStartY, letterHeight, widthPerAlphabet)
        }
  	  	tics[colIdx] = letterStartX + (widthPerAlphabet) / 2
    }
  	grid.lines(x = unit(c(0,max_x),"native"),y = unit(c(0,0),"native"))
  	grid.lines(x = unit(c(0,max_x),"native"),y = unit(c(biasToPlot,biasToPlot),"native"),gp=gpar(lty="dashed"))
  	grid.polygon(x = unit(letters$x, "native"), y = unit(letters$y, "native"), id = letters$id, gp = gpar(fill = letters$fill, col = "transparent")) 
    grid.xaxis(at = tics,  label = 1:motifLength, gp = gpar(fontsize = 15))
    grid.yaxis()
  	grid.text("Position",  y = unit(-3, "lines"), gp = gpar(fontsize = 15))
    dev.off()
}

args <- commandArgs(trailingOnly = TRUE)
fileWithMotif <- args[1]
outfile <- args[2]
bias <- as.integer(args[3])
plotConvFilter(fileWithMotif, outfile, bias)
