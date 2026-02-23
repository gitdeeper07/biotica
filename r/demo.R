#' BIOTICA Demo
#' 
#' Simple demonstration of BIOTICA R package

library(biotica)

cat("\n=== BIOTICA Demo ===\n\n")

# IBR example
cat("1. Computing IBR:\n")
params <- list(VCA = 0.85, MDI = 0.78, PTS = 0.82)
result <- ibr_composite(params)
print(result)

# Tipping point example
cat("\n2. Detecting tipping points:\n")
x <- cumsum(rnorm(100))
tipping <- tipping_points(x)
print(tipping)

cat("\nDemo completed.\n")
