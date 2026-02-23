#' Compare IBR Scores Across Multiple Plots
#'
#' @param plot_data Data frame with plot IDs and IBR scores
#' @param main Title for the plot
#' @return None (creates plot)
#' @export
#'
#' @examples
#' plots <- data.frame(id=1:10, ibr=runif(10))
#' compare_plots(plots)

compare_plots <- function(plot_data, main = "IBR Score Comparison") {
  if (!"ibr" %in% names(plot_data)) {
    stop("Data must contain 'ibr' column")
  }
  
  if (!"id" %in% names(plot_data)) {
    plot_data$id <- 1:nrow(plot_data)
  }
  
  # Sort by IBR score
  plot_data <- plot_data[order(plot_data$ibr), ]
  
  # Create barplot
  barplot(plot_data$ibr,
          names.arg = plot_data$id,
          main = main,
          xlab = "Plot ID",
          ylab = "IBR Score",
          col = "steelblue",
          las = 2,
          ylim = c(0, 1))
  
  # Add threshold lines
  abline(h = 0.88, col = "darkgreen", lty = 2, lwd = 2)
  abline(h = 0.75, col = "green", lty = 2, lwd = 2)
  abline(h = 0.60, col = "orange", lty = 2, lwd = 2)
  abline(h = 0.45, col = "red", lty = 2, lwd = 2)
  
  legend("topright",
         legend = c("Pristine", "Functional", "Impaired", "Degraded"),
         col = c("darkgreen", "green", "orange", "red"),
         lty = 2, lwd = 2, cex = 0.8)
}
