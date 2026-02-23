#' Detect Tipping Points
#' @param x Time series
#' @return Tipping point result
#' @export
tipping_points <- function(x) {
  n <- length(x)
  var_trend <- cor(1:(n-20), sapply(1:(n-20), function(i) var(x[i:(i+20)])))
  
  structure(list(
    variance_trend = var_trend,
    warning = ifelse(var_trend > 0.2, "WARNING", "OK")
  ), class = "tipping")
}

#' @export
print.tipping <- function(x, ...) {
  cat("Tipping Point Analysis\n")
  cat("Variance trend:", round(x$variance_trend, 3), "\n")
  cat("Status:", x$warning, "\n")
}
