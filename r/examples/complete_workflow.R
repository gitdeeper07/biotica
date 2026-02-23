#' Complete BIOTICA Workflow Example
#' 
#' This script demonstrates a complete workflow using all BIOTICA R functions

library(biotica)

# Generate sample ecosystem data
set.seed(42)
n <- 100

ecosystem_data <- data.frame(
  plot_id = 1:n,
  VCA = rbeta(n, 5, 2),
  MDI = rbeta(n, 4, 2),
  PTS = rbeta(n, 3, 2),
  HFI = rbeta(n, 4, 3),
  BNC = rbeta(n, 3, 2),
  SGH = rbeta(n, 3, 3),
  AES = rbeta(n, 6, 1),
  TMI = rbeta(n, 4, 3),
  RRC = rbeta(n, 3, 4),
  biome = sample(c("Forest", "Grassland", "Wetland"), n, replace = TRUE)
)

cat("\n=== Step 1: Descriptive Statistics ===\n")
stats <- ecosystem_stats(ecosystem_data[, 2:10])
print(stats)

cat("\n=== Step 2: Correlation Analysis ===\n")
correlations <- parameter_correlation(ecosystem_data[, 2:10])
print(correlations)

cat("\n=== Step 3: IBR Computation for Each Plot ===\n")
ibr_scores <- numeric(n)
for (i in 1:n) {
  params <- as.list(ecosystem_data[i, 2:10])
  result <- ibr_composite(params)
  ibr_scores[i] <- result$score
}

ecosystem_data$IBR <- ibr_scores
cat(sprintf("Mean IBR: %.3f\n", mean(ibr_scores)))
cat(sprintf("SD IBR: %.3f\n", sd(ibr_scores)))

cat("\n=== Step 4: IBR Distribution ===\n")
hist(ibr_scores, breaks = 20, main = "IBR Distribution", xlab = "IBR Score")

cat("\n=== Step 5: Bayesian Weight Estimation ===\n")
weight_data <- ecosystem_data[, c("VCA", "MDI", "PTS", "HFI", "BNC", "SGH", "AES", "TMI", "RRC", "IBR")]
weights <- bayesian_weights_complete(weight_data)
print(weights)

cat("\n=== Step 6: Time Series Analysis (Example) ===\n")
# Create synthetic time series for one plot
time_series <- cumsum(rnorm(200)) + 10
ts_result <- analyze_timeseries(time_series, frequency = 12)
print(ts_result)

cat("\n=== Workflow Complete ===\n")
