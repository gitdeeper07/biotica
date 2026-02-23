#' Generate sample data for BIOTICA package

set.seed(42)

Create sample ecosystem data

n <- 100

sample_data <- data.frame(
plot_id = 1:n,
VCA = runif(n, 0.5, 0.9),
MDI = runif(n, 0.5, 0.9),
PTS = runif(n, 0.5, 0.9),
HFI = runif(n, 0.5, 0.9),
BNC = runif(n, 0.5, 0.9),
SGH = runif(n, 0.5, 0.9),
AES = runif(n, 0.5, 0.9),
TMI = runif(n, 0.5, 0.9),
RRC = runif(n, 0.5, 0.9),
biome = sample(c("Forest", "Grassland", "Wetland"), n, replace = TRUE)
)

Save to R data format

save(sample_data, file = "data/sample_data.rda")
