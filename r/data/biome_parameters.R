#' Biome-specific parameters for BIOTICA
#'
#' Reference values for different biome types
#'
#' @format A list with biome parameters
"biome_parameters"

# Create biome parameters
biome_parameters <- list(
  tropical_forest = list(
    VCA = list(min = 0.75, max = 0.95, ref = 0.88),
    MDI = list(min = 0.80, max = 0.98, ref = 0.92),
    PTS = list(min = 0.70, max = 0.92, ref = 0.85),
    HFI = list(min = 0.65, max = 0.88, ref = 0.82),
    BNC = list(min = 0.72, max = 0.94, ref = 0.86),
    SGH = list(min = 0.68, max = 0.90, ref = 0.84),
    AES = list(min = 0.55, max = 0.92, ref = 0.78),
    TMI = list(min = 0.65, max = 0.91, ref = 0.83),
    RRC = list(min = 0.50, max = 0.88, ref = 0.75)
  ),
  temperate_forest = list(
    VCA = list(min = 0.65, max = 0.88, ref = 0.80),
    MDI = list(min = 0.70, max = 0.92, ref = 0.85),
    PTS = list(min = 0.60, max = 0.85, ref = 0.75),
    HFI = list(min = 0.62, max = 0.86, ref = 0.78),
    BNC = list(min = 0.68, max = 0.90, ref = 0.82),
    SGH = list(min = 0.63, max = 0.87, ref = 0.79),
    AES = list(min = 0.48, max = 0.88, ref = 0.72),
    TMI = list(min = 0.60, max = 0.86, ref = 0.77),
    RRC = list(min = 0.45, max = 0.84, ref = 0.70)
  ),
  grassland = list(
    VCA = list(min = 0.50, max = 0.80, ref = 0.70),
    MDI = list(min = 0.60, max = 0.88, ref = 0.78),
    PTS = list(min = 0.55, max = 0.80, ref = 0.72),
    HFI = list(min = 0.48, max = 0.78, ref = 0.68),
    BNC = list(min = 0.55, max = 0.82, ref = 0.75),
    SGH = list(min = 0.52, max = 0.80, ref = 0.73),
    AES = list(min = 0.45, max = 0.85, ref = 0.68),
    TMI = list(min = 0.48, max = 0.75, ref = 0.71),
    RRC = list(min = 0.48, max = 0.82, ref = 0.72)
  )
)

save(biome_parameters, file = "data/biome_parameters.rda")
