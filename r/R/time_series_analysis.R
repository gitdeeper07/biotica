#' Advanced Time Series Analysis for Ecosystem Data
#'
#' @param x Time series vector
#' @param frequency Seasonal frequency (e.g., 12 for monthly)
#' @return List with decomposition and trend analysis
#' @export
#'
#' @examples
#' x <- cumsum(rnorm(120))
#' ts_analysis <- analyze_timeseries(x, frequency=12)

analyze_timeseries <- function(x, frequency = 1) {
  # Convert to ts object
  if (frequency > 1) {
    x_ts <- ts(x, frequency = frequency)
    
    # Decompose if possible
    decomp <- tryCatch({
      stl(x_ts, s.window = "periodic")
    }, error = function(e) NULL)
  } else {
    decomp <- NULL
    x_ts <- ts(x)
  }
  
  # Trend analysis
  n <- length(x)
  trend <- lm(x ~ I(1:n))
  
  # Autocorrelation
  acf_val <- acf(x, plot = FALSE, lag.max = 1)$acf[2]
  
  result <- list(
    mean = mean(x),
    sd = sd(x),
    trend_slope = coef(trend)[2],
    trend_p_value = summary(trend)$coefficients[2, 4],
    acf_lag1 = acf_val,
    decomposition = decomp,
    frequency = frequency,
    length = n
  )
  
  class(result) <- "timeseries_analysis"
  return(result)
}

#' Print timeseries_analysis object
#' @param x Object of class timeseries_analysis
#' @param ... Additional arguments
#' @export

print.timeseries_analysis <- function(x, ...) {
  cat("Time Series Analysis\n")
  cat("===================\n")
  cat(sprintf("Length: %d\n", x$length))
  cat(sprintf("Mean: %.3f\n", x$mean))
  cat(sprintf("SD: %.3f\n", x$sd))
  cat(sprintf("Trend slope: %.4f (p=%.4f)\n", x$trend_slope, x$trend_p_value))
  cat(sprintf("Lag-1 ACF: %.3f\n", x$acf_lag1))
  invisible(x)
}
