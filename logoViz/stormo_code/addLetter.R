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

