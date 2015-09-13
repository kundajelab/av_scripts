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

