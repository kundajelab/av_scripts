library(grid)

letterA <-
function (x.pos, y.pos, ht, wt, id = NULL) {
    x <- c(0, 4, 6, 10, 8, 6.8, 3.2, 2, 0, 3.6, 5, 6.4, 3.6)
    y <- c(0, 10, 10, 0, 0, 3, 3, 0, 0, 4, 7.5, 4, 4)
    x <- 0.1 * x
    y <- 0.1 * y
    x <- x.pos + wt * x
    y <- y.pos + ht * y
    if (is.null(id)) {
        id <- c(rep(1, 9), rep(2, 4))
    }
    else {
        id <- c(rep(id, 9), rep(id + 1, 4))
    }
    fill <- c(rgb(0, 0.6, 0.5), "white")
    list(x = x, y = y, id = id, fill = fill)
}

letterC <-
function (x.pos, y.pos, ht, wt, id = NULL) {
    angle1 <- seq(0.3 + pi/2, pi, length = 100)
    angle2 <- seq(pi, 1.5 * pi, length = 100)
    x.l1 <- 0.5 + 0.5 * sin(angle1)
    y.l1 <- 0.5 + 0.5 * cos(angle1)
    x.l2 <- 0.5 + 0.5 * sin(angle2)
    y.l2 <- 0.5 + 0.5 * cos(angle2)
    x.l <- c(x.l1, x.l2)
    y.l <- c(y.l1, y.l2)
    x <- c(x.l, rev(x.l))
    y <- c(y.l, 1 - rev(y.l))
    x.i1 <- 0.5 + 0.35 * sin(angle1)
    y.i1 <- 0.5 + 0.35 * cos(angle1)
    x.i1 <- x.i1[y.i1 <= max(y.l1)]
    y.i1 <- y.i1[y.i1 <= max(y.l1)]
    y.i1[1] <- max(y.l1)
    x.i2 <- 0.5 + 0.35 * sin(angle2)
    y.i2 <- 0.5 + 0.35 * cos(angle2)
    x.i <- c(x.i1, x.i2)
    y.i <- c(y.i1, y.i2)
    x1 <- c(x.i, rev(x.i))
    y1 <- c(y.i, 1 - rev(y.i))
    x <- c(x, rev(x1))
    y <- c(y, rev(y1))
    x <- x.pos + wt * x
    y <- y.pos + ht * y
    if (is.null(id)) {
        id <- rep(1, length(x))
    }
    else {
        id <- rep(id, length(x))
    }
    fill <- rgb(0.35,0.7,0.9)
    list(x = x, y = y, id = id, fill = fill)
}

letterG <-
function (x.pos, y.pos, ht, wt, id = NULL) {
    angle1 <- seq(0.3 + pi/2, pi, length = 100)
    angle2 <- seq(pi, 1.5 * pi, length = 100)
    x.l1 <- 0.5 + 0.5 * sin(angle1)
    y.l1 <- 0.5 + 0.5 * cos(angle1)
    x.l2 <- 0.5 + 0.5 * sin(angle2)
    y.l2 <- 0.5 + 0.5 * cos(angle2)
    x.l <- c(x.l1, x.l2)
    y.l <- c(y.l1, y.l2)
    x <- c(x.l, rev(x.l))
    y <- c(y.l, 1 - rev(y.l))
    x.i1 <- 0.5 + 0.35 * sin(angle1)
    y.i1 <- 0.5 + 0.35 * cos(angle1)
    x.i1 <- x.i1[y.i1 <= max(y.l1)]
    y.i1 <- y.i1[y.i1 <= max(y.l1)]
    y.i1[1] <- max(y.l1)
    x.i2 <- 0.5 + 0.35 * sin(angle2)
    y.i2 <- 0.5 + 0.35 * cos(angle2)
    x.i <- c(x.i1, x.i2)
    y.i <- c(y.i1, y.i2)
    x1 <- c(x.i, rev(x.i))
    y1 <- c(y.i, 1 - rev(y.i))
    x <- c(x, rev(x1))
    y <- c(y, rev(y1))
    h1 <- max(y.l1)
    r1 <- max(x.l1)
    h1 <- 0.4
    x.add <- c(r1, 0.5, 0.5, r1 - 0.2, r1 - 0.2, r1, r1)
    y.add <- c(h1, h1, h1 - 0.1, h1 - 0.1, 0, 0, h1)
    if (is.null(id)) {
        id <- c(rep(1, length(x)), rep(2, length(x.add)))
    }
    else {
        id <- c(rep(id, length(x)), rep(id + 1, length(x.add)))
    }
    x <- c(rev(x), x.add)
    y <- c(rev(y), y.add)
    x <- x.pos + wt * x
    y <- y.pos + ht * y
    fill <- c(rgb(0.9, 0.6, 0), rgb(0.9, 0.6, 0))
    list(x = x, y = y, id = id, fill = fill)
}

letterT <-
function (x.pos, y.pos, ht, wt, id = NULL) {
    x <- c(0, 10, 10, 6, 6, 4, 4, 0)
    y <- c(10, 10, 9, 9, 0, 0, 9, 9)
    x <- 0.1 * x
    y <- 0.1 * y
    x <- x.pos + wt * x
    y <- y.pos + ht * y
    if (is.null(id)) {
        id <- rep(1, 8)
    }
    else {
        id <- rep(id, 8)
    }
    fill <- rgb(0.1, 0.1, 0.1)
    list(x = x, y = y, id = id, fill = fill)
}

addLetter <-
function (letters, which, x.pos, y.pos, ht, wt) {
    if (which == "A") {
        letter <- letterA(x.pos, y.pos, ht, wt)
    }
    else if (which == "C") {
        letter <- letterC(x.pos, y.pos, ht, wt)
    }
    else if (which == "G") {
        letter <- letterG(x.pos, y.pos, ht, wt)
    }
    else if (which == "T") {
        letter <- letterT(x.pos, y.pos, ht, wt)
    }
    else {
        stop("which must be one of A,C,G,T")
    }
    letters$x <- c(letters$x, letter$x)
    letters$y <- c(letters$y, letter$y)
    lastID <- ifelse(is.null(letters$id), 0, max(letters$id))
    letters$id <- c(letters$id, lastID + letter$id)
    letters$fill <- c(letters$fill, letter$fill)
    letters
}

plotValues <- function (fileWithMotif, outfile, bias) {
    motifMatrix = as.matrix(read.table(fileWithMotif))
    motifLength = dim(motifMatrix)[1]
    biasByMotifLength = bias/motifLength 
    maximumHeight = max(biasByMotifLength,max(rowSums(motifMatrix*(motifMatrix>=0))))
    minimumHeight = min(biasByMotifLength,min(0,min(rowSums(motifMatrix*(motifMatrix<0)))))
    #make a png of the appropriate height
    widthPerAlphabet = 1
    letterOrdering = c("A","C","G","T")
    letters <- list(x = NULL, y = NULL, id = NULL, fill = NULL)
    
  	tics = rep(0, motifLength)
    png(file=outfile, width=50*motifLength, height=500, units="px")
    grid.newpage()
    fontsize=15
    margin=0.1*(motifLength)+(fontsize/3.5)
  	pvp=plotViewport(c(margin, margin, margin, margin), name = "vp_margins")
    pushViewport(pvp)
    max_x = motifLength*widthPerAlphabet;
  	pushViewport(dataViewport(seq(0,max_x,0.01), seq(minimumHeight*1.01,maximumHeight,0.01), name = "vp_data"))
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
  	grid.lines(x = unit(c(0,max_x),"native"),y = unit(c(biasByMotifLength,biasByMotifLength),"native"),gp=gpar(lty="dashed"))
  	grid.polygon(x = unit(letters$x, "native"), y = unit(letters$y, "native"), id = letters$id, gp = gpar(fill = letters$fill, col = "transparent")) 
    grid.xaxis(at = tics,  label = 1:motifLength, gp = gpar(fontsize = 15))
    grid.yaxis()
  	grid.text("Position",  y = unit(-3, "lines"), gp = gpar(fontsize = 15))
    dev.off()
}

#args <- commandArgs(trailingOnly = TRUE)
#fileWithMotif <- args[1]
#plotValues(fileWithMotif)

