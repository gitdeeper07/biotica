#' Analyze Food Web Structure
#'
#' @param interactions Matrix of species interactions
#' @return List with food web metrics
#' @export
#'
#' @examples
#' mat <- matrix(rbinom(100, 1, 0.1), 10, 10)
#' food_web_analysis(mat)

food_web_analysis <- function(interactions) {
  n_species <- nrow(interactions)
  
  # Calculate metrics
  connectance <- sum(interactions) / (n_species^2)
  links_per_species <- sum(interactions) / n_species
  
  # Trophic levels (simplified)
  in_degree <- colSums(interactions)
  out_degree <- rowSums(interactions)
  
  result <- list(
    n_species = n_species,
    n_links = sum(interactions),
    connectance = connectance,
    links_per_species = links_per_species,
    mean_in_degree = mean(in_degree),
    mean_out_degree = mean(out_degree)
  )
  
  class(result) <- "food_web"
  return(result)
}

#' Print food web analysis
#' @param x Food web object
#' @param ... Additional arguments
#' @export

print.food_web <- function(x, ...) {
  cat("Food Web Analysis\n")
  cat("================\n")
  cat(sprintf("Species: %d\n", x$n_species))
  cat(sprintf("Links: %d\n", x$n_links))
  cat(sprintf("Connectance: %.3f\n", x$connectance))
  cat(sprintf("Links per species: %.2f\n", x$links_per_species))
  invisible(x)
}
