EnergyLogo <-
function(ener.vector, main=NULL, width.pwm = 1, width.di = 0.125, width.spacer=0.01, x.tic.loc=NULL, xaxis=T, yaxis=T, xfontsize=15, yfontsize=15,y.min = NULL, y.max=NULL, xlabel="Positions", ylabel="-E", width.img=1000, height.img=600) {

  	alph = c("A","C","G","T")
  	#Number of mono-nucleotide positions in the given Binding Energy Model 
  	npos = (length(ener.vector) + 16) / 20
  	
  	#Mono-nucleotide start and end position
  	pwm.start = 1
  	pwm.end = 4*npos
  	#Di-nucleotide start and end position	
  	di.nuc.start = pwm.end+1
  	di.nuc.end = di.nuc.start + 16*(npos-1)-1
  	
  	# make sure energy matrices have column mean of 0
  	pwm = apply(matrix(ener.vector[pwm.start:pwm.end],4), 2, function(x) x-mean(x))
  	di.nuc = apply(matrix(ener.vector[di.nuc.start:di.nuc.end],16), 2, function(x) x-mean(x))
  	
  	# width of pwm positions are set to 1, di-nuc positions are 0.1 each (0.2 for the entire di-nucleotide pos)
  	letters <- list(x = NULL, y = NULL, id = NULL, fill = NULL)
  	
  	x.pos = 0
  	x.tics = rep(0, npos)

  	## figure out the height and width of all the letters
  	
  	## specify positions of letters
  	for (j in 1:(ncol(pwm)-1)) {
  	  	column = pwm[,j]
  	  	letterOrder = order(column,4:1)
  	  	col.min = sum(column[column<0])
  	  	y.pos = col.min-(sum(column<0)-1)*width.spacer

  	 	for (i in 1:4) {
  	    		letter = alph[letterOrder[i]]
  	    		ht = abs(column[letterOrder[i]])
  	    		if (ht > 0) letters <- addLetter(letters, letter, x.pos, y.pos, ht, width.pwm)
  	    		y.pos <- y.pos + ht + width.spacer
  	  	}
  	  	x.tics[j] = x.pos + (width.pwm + width.spacer) / 2
  	  	x.pos = x.pos + width.pwm + width.spacer

  	  	## if di-nucleotide energies are non-zero, plot them. other wise skip
  	  	if (sum(di.nuc[,j] != 0)) {
  	    		column = di.nuc[,j]
  	    		letterOrder = order(column,16:1)
  	    		col.min = sum(column[column<0])
  	    		y.pos = col.min-(sum(column<0)-1)*width.spacer
  	  
  	    		for ( i in 1:16) {
  	      			letter = rep(alph, each=4)[letterOrder][i]
  	      			ht = abs(di.nuc[letterOrder,j][i])
  	      			if (ht > 0) letters <- addLetter(letters, letter, x.pos, y.pos, ht, width.di)
  	      			y.pos <- y.pos + ht + width.spacer
  	    		}

  	    		y.pos = col.min-(sum(column<0)-1)*width.spacer
  	    		x.pos = x.pos + width.di + width.spacer
  	    		for ( i in 1:16) {
  	      			letter = rep(alph, times=4)[letterOrder][i]
  	      			ht = abs(di.nuc[letterOrder,j][i])
  	      			if (ht > 0) letters <- addLetter(letters, letter, x.pos, y.pos, ht, width.di)
  	      			y.pos <- y.pos + ht + width.spacer
  	    		}
  	    		x.pos = x.pos + width.di + width.spacer      
  	  	}
  	}
  	## last position of PWM
  	j = ncol(pwm)
  	column = pwm[,j]
  	letterOrder = order(column,4:1)
  	col.min = sum(column[column<0])
  	y.pos = col.min-(sum(column<0)-1)*width.spacer
  	for (i in 1:4) {
  	  	letter = alph[letterOrder[i]]
  	  	ht = abs(column[letterOrder[i]])
  	  	if (ht > 0) letters <- addLetter(letters, letter, x.pos, y.pos, ht, width.pwm)
  	  	y.pos <- y.pos + ht +width.spacer
  	}
  	x.tics[j] = x.pos + width.pwm/2
  	
  	y.min = min(apply(pwm,2,function(x) sum(x[x<0])), apply(di.nuc,2,function(x) sum(x[x<0])))
  	y.max = max(apply(pwm,2,function(x) sum(x[x>0])), apply(di.nuc,2,function(x) sum(x[x>0])))
  	x.max = x.tics[j] + width.pwm/2 + width.spacer
  	
  	outfile = paste("./SeqLogos/", main, ".png", sep="")
	png(file=outfile, width=width.img, height=height.img, units="px")
	grid.newpage()
  	leftMargin = ifelse(yaxis, 2 + yfontsize/3.5, 2)
  	bottomMargin = ifelse(xaxis, 2 + xfontsize/3.5, 2)
  	topMargin = ifelse(!is.null(main), 3, 2)
  	
  	pushViewport(plotViewport(c(bottomMargin, leftMargin, topMargin, 2), name = "vp_margins"))
  	pushViewport(dataViewport(seq(0,x.max,0.01), seq(y.min,y.max,0.01), name = "vp_data"))

  	grid.lines(x = unit(c(0,x.max),"native"),y = unit(c(0,0),"native"),gp=gpar(lty="dashed"))
  	grid.polygon(x = unit(letters$x, "native"), y = unit(letters$y, "native"), id = letters$id, gp = gpar(fill = letters$fill, col = "transparent"))

  	if (xaxis) {
  		x.tic.loc = x.tics
  	    	x.lab = 1:npos
  	    	x.txt = xlabel
  	}
  	grid.xaxis(at = x.tic.loc,  label = x.lab, gp = gpar(fontsize = xfontsize))
  	grid.text(x.txt,  y = unit(-3, "lines"), gp = gpar(fontsize = xfontsize))

  	if (yaxis) {
 		grid.yaxis(gp = gpar(fontsize = yfontsize))
  	  	y.txt = ylabel
  	  	grid.text(y.txt, x = unit(-3, "lines"), rot = 90, gp = gpar(fontsize = yfontsize))
  	}
  	
  	#popViewport()
  	if (!is.null(main)) grid.text(main, y = unit(1, "npc") + unit(0.4, "lines"), gp = gpar(fontsize = xfontsize+10))
  	#popViewport()
	dev.off() 
  	par(ask = FALSE)
}

