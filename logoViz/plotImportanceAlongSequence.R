#!/usr/bin/env Rscript
library(grid)
pathPrefix = paste(Sys.getenv(x = "UTIL_SCRIPTS_DIR", unset = "", names = NA),"/logoViz",sep="")
stormoPathPrefix = paste(pathPrefix,"/stormo_code",sep="")
source(paste(stormoPathPrefix,"/letterA.R",sep=""))
source(paste(stormoPathPrefix,"/letterC.R",sep=""))
source(paste(stormoPathPrefix,"/letterG.R",sep=""))
source(paste(stormoPathPrefix,"/letterT.R",sep=""))
source(paste(stormoPathPrefix,"/addLetter.R",sep=""))


plotImportanceAlongSequence <- function (fileWithImportances, outfile) {
    library(Cairo)
    motifMatrix = as.matrix(read.table(fileWithImportances)) #rows are ACGT, cols are position
    motifLength = dim(motifMatrix)[1]
    theRowSums = rowSums(motifMatrix)
    maximumHeight = max(theRowSums)
    minimumHeight = min(0,min(rowSums(motifMatrix*(motifMatrix<0))))
    #make a png of the appropriate height
    widthPerAlphabet = 1
    letterOrdering = c("A","C","G","T")
    letters <- list(x = NULL, y = NULL, id = NULL, fill = NULL) 
  	tics = rep(0, motifLength)
    CairoPNG(file=outfile, width=5*motifLength, height=2000, units="px")
    options(bitmapType='cairo')
    #png(file=outfile, width=50*motifLength, height=2000, units="px")
    grid.newpage()
    fontsize=15
    margin=5
  	pvp=plotViewport(c(5, 5, 5, 5), name = "vp_margins")
    pushViewport(pvp)
    max_x = motifLength*widthPerAlphabet;
    print(minimumHeight)
  	pushViewport(dataViewport(seq(0,max_x,0.01), seq(minimumHeight*1.01,maximumHeight,0.0001), name = "vp_data"))
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
        #for (letterIdx in 1:4) {
        #    theLetter = letterOrdering[letterIdx];
        #    letterHeight = thisColumn[letterIdx]
        #    if (letterHeight != 0) {
        #        if (letterHeight != theRowSums[colIdx]) {
        #           print(paste("Not supposed to have more than one nonzero entry per column! Issue with column",colIdx,letterHeight,theRowSums[colIdx]))
        #        }
        #        letterStartY=0
        #        letters=addLetter(letters,theLetter, letterStartX, letterStartY, letterHeight, widthPerAlphabet)
        #    }
        #}
  	  	tics[colIdx] = letterStartX + (widthPerAlphabet) / 2
    }
  	grid.lines(x = unit(c(0,max_x),"native"),y = unit(c(0,0),"native"))
  	grid.polygon(x = unit(letters$x, "native"), y = unit(letters$y, "native"), id = letters$id, gp = gpar(fill = letters$fill, col = "transparent")) 
    grid.xaxis(at = tics,  label = 1:motifLength, gp = gpar(fontsize = fontsize))
    grid.yaxis()
    dev.off()
}

args <- commandArgs(trailingOnly = TRUE)
fileWithImportances <- args[1]
outfile <- args[2]
plotImportanceAlongSequence(fileWithImportances, outfile)
