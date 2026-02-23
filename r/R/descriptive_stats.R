#' Descriptive Statistics for Ecosystem Parameters
#'
#' @param data Data frame with parameter columns
#' @return List of statistics
#' @export
#'
#' @examples
#' data <- data.frame(VCA=runif(100), MDI=runif(100))
#' stats <- ecosystem_stats(data)

ecosystem_stats <- function(data) {
  results <- list()
  
  for (col in names(data)) {
    if (is.numeric(data[[col]])) {
      results[[col]] <- list(
        mean = mean(data[[col]], na.rm = TRUE),
        sd = sd(data[[col]], na.rm = TRUE),
        min = min(data[[col]], na.rm = TRUE),
        max = max(data[[col]], na.rm = TRUE),
        q25 = quantile(data[[col]], 0.25, na.rm = TRUE),
        q50 = median(data[[col]], na.rm = TRUE),
        q75 = quantile(data[[col]], 0.75, na.rm = TRUE),
        na_count = sum(is.na(data[[col]]))
      )
    }
  }
  
  class(results) <- "ecosystem_stats"
  return(results)
}

#' Print ecosystem_stats object
#' @param x Object of class ecosystem_stats
#' @param ... Additional arguments
#' @export

print.ecosystem_stats <- function(x, ...) {
  cat("Ecosystem Statistics\n")
  cat("===================\n")
  
  for (param in names(x)) {
    cat(sprintf("\n%s:\n", param))
    cat(sprintf("  Mean: %.3f\n", x[[param]]$mean))
    cat(sprintf("  SD: %.3f\n", x[[param]]$sd))
    cat(sprintf("  Range: [%.3f, %.3f]\n", x[[param]]$min, x[[param]]$max))
    cat(sprintf("  Quartiles: %.3f - %.3f - %.3f\n",
                x[[param]]$q25, x[[param]]$q50, x[[param]]$q75))
  }
}
