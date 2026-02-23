#' Advanced Visualization Examples
#' 
#' This script demonstrates advanced plotting with BIOTICA

library(biotica)
library(graphics)

# Generate sample data
set.seed(42)
n_plots <- 30
n_time <- 50

# Create time series for multiple plots
time_series <- matrix(NA, nrow = n_time, ncol = n_plots)
for (i in 1:n_plots) {
  # Each plot has slightly different dynamics
  base <- runif(1, 0.5, 0.8)
  trend <- rnorm(1, 0, 0.01)
  noise <- rnorm(n_time, 0, 0.05)
  time_series[, i] <- base + (1:n_time) * trend + noise
  time_series[, i] <- pmax(pmin(time_series[, i], 1), 0)  # Clip to [0,1]
}

# 1. Plot multiple time series
cat("\n=== Plot 1: Multiple Time Series ===\n")
plot(time_series[, 1], type = "l", col = 1, 
     ylim = range(time_series),
     xlab = "Time", ylab = "Value",
     main = "Ecosystem Time Series")
for (i in 2:n_plots) {
  lines(time_series[, i], col = i)
}

# 2. IBR comparison across plots
cat("\n=== Plot 2: IBR Comparison ===\n")
ibr_values <- apply(time_series, 2, mean)
plot_data <- data.frame(
  id = 1:n_plots,
  ibr = ibr_values
)
compare_plots(plot_data, main = "IBR Scores Across Plots")

# 3. Correlation heatmap (simplified)
cat("\n=== Plot 3: Correlation Matrix ===\n")
cor_matrix <- cor(time_series[, 1:10])
image(1:10, 1:10, cor_matrix, 
      main = "Correlation Matrix",
      xlab = "Plot", ylab = "Plot",
      col = heat.colors(12))

# 4. IBR distribution
cat("\n=== Plot 4: IBR Distribution ===\n")
hist(ibr_values, breaks = 15,
     main = "Distribution of IBR Scores",
     xlab = "IBR Score", ylab = "Frequency",
     col = "lightblue")

cat("\n✓ All visualizations complete\n")
