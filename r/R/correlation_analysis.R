#' Correlation Analysis for Ecosystem Parameters
#'
#' @param data Data frame with parameter columns
#' @param method Correlation method ("pearson", "spearman", "kendall")
#' @return Correlation matrix
#' @export
#'
#' @examples
#' data <- data.frame(VCA=runif(100), MDI=runif(100), IBR=runif(100))
#' corr <- parameter_correlation(data)

parameter_correlation <- function(data, method = "pearson") {
  # Select only numeric columns
  numeric_cols <- sapply(data, is.numeric)
  data_numeric <- data[, numeric_cols, drop = FALSE]
  
  # Compute correlation matrix
  cor_matrix <- cor(data_numeric, method = method, use = "complete.obs")
  
  # Compute p-values
  p_matrix <- matrix(NA, ncol(cor_matrix), ncol(cor_matrix))
  for (i in 1:ncol(cor_matrix)) {
    for (j in 1:ncol(cor_matrix)) {
      if (i != j) {
        test <- cor.test(data_numeric[, i], data_numeric[, j], method = method)
        p_matrix[i, j] <- test$p.value
      }
    }
  }
  
  colnames(p_matrix) <- colnames(cor_matrix)
  rownames(p_matrix) <- colnames(cor_matrix)
  
  result <- list(
    correlation = cor_matrix,
    p_value = p_matrix,
    method = method,
    n = nrow(data_numeric)
  )
  
  class(result) <- "parameter_correlation"
  return(result)
}

#' Print parameter_correlation object
#' @param x Object of class parameter_correlation
#' @param ... Additional arguments
#' @export

print.parameter_correlation <- function(x, ...) {
  cat("Parameter Correlation Analysis\n")
  cat("==============================\n")
  cat("Method:", x$method, "\n")
  cat("Sample size:", x$n, "\n\n")
  cat("Correlation matrix:\n")
  print(round(x$correlation, 3))
  
  # Show significant correlations
  sig_corrs <- which(x$p_value < 0.05 & !is.na(x$p_value), arr.ind = TRUE)
  if (nrow(sig_corrs) > 0) {
    cat("\nSignificant correlations (p < 0.05):\n")
    for (i in 1:nrow(sig_corrs)) {
      r <- sig_corrs[i, 1]
      c <- sig_corrs[i, 2]
      if (r < c) {  # Avoid duplicates
        cat(sprintf("  %s - %s: r = %.3f, p = %.4f\n",
                    rownames(x$correlation)[r],
                    colnames(x$correlation)[c],
                    x$correlation[r, c],
                    x$p_value[r, c]))
      }
    }
  }
}
