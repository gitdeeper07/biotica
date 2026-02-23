#' Basic BIOTICA R Package Example
#' 
#' Simple example showing core functionality

library(biotica)

# Example 1: Basic IBR computation
params <- list(
  VCA = 0.85,
  MDI = 0.78,
  PTS = 0.82
)

result <- ibr_composite(params)
print(result)

# Example 2: Tipping point detection
set.seed(42)
timeseries <- cumsum(rnorm(100))
tipping <- tipping_points(timeseries, window = 20)
print(tipping)

# Example 3: Parameter validation
valid <- validate_parameters(params)
cat("Parameters valid:", valid, "\n")
