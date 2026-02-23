#' Utility functions for BIOTICA R package
#'
#' @param x Input value
#' @return Normalized value
#' @export

normalize <- function(x, min_val = 0, max_val = 1) {
  (x - min_val) / (max_val - min_val)
}

#' @export
clip <- function(x, min_val = 0, max_val = 1) {
  pmax(pmin(x, max_val), min_val)
}

#' @export
weighted_sum <- function(values, weights) {
  sum(values * weights, na.rm = TRUE)
}
