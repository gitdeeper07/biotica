#' Plot IBR Results
#'
#' @param x IBR result object
#' @param ... Additional plotting arguments
#' @export
#'
#' @examples
#' params <- list(VCA=0.85, MDI=0.78, PTS=0.82)
#' result <- ibr_composite(params)
#' plot_ibr(result)

plot_ibr <- function(x, ...) {
  if (!inherits(x, "ibr_result")) {
    stop("Object must be of class 'ibr_result'")
  }
  
  contributions <- unlist(x$contributions)
  
  barplot(contributions,
          main = paste("IBR Score:", round(x$score, 3)),
          xlab = "Parameters",
          ylab = "Contribution",
          col = "steelblue",
          las = 2,
          ...)
  
  abline(h = x$score, col = "red", lty = 2, lwd = 2)
  legend("topright", legend = "IBR Score", col = "red", lty = 2, lwd = 2)
}

#' Plot tipping point analysis
#' @param x Tipping point result object
#' @param timeseries Original time series
#' @param ... Additional arguments
#' @export

plot_tipping <- function(x, timeseries, ...) {
  if (!inherits(x, "tipping_result")) {
    stop("Object must be of class 'tipping_result'")
  }
  
  par(mfrow = c(2, 1))
  
  # Plot time series
  plot(timeseries, type = "l", main = "Time Series", xlab = "Time", ylab = "Value")
  
  # Plot warning level
  barplot(x$warning_level,
          main = paste("Warning Level:", x$warning_level),
          xlab = "",
          ylab = "Level",
          col = ifelse(x$critical_slowing_down, "red", "gray"))
  
  par(mfrow = c(1, 1))
}
