for (i in 1:num) {
    filename = paste("pr",i,".png",sep="")
    png(filename)
    barplot(components$rotation[,i])
    dev.off()
    filename = paste("hist_projection_pr",i,".png",sep="")
    png(filename)
    hist(components$x[,i])
    dev.off()
}
