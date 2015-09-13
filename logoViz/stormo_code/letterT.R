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

