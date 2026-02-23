# BIOTICA R Package

R package for BIOTICA statistical analysis.

## Installation

```r
install.packages("path/to/biotica", repos = NULL, type = "source")
```

Quick Example

```r
library(biotica)
params <- list(VCA = 0.85, MDI = 0.78)
result <- ibr_composite(params)
print(result)
```

Functions

· ibr_composite(): IBR index calculation
· tipping_points(): Tipping point detection
· validate_parameters(): Parameter validation
