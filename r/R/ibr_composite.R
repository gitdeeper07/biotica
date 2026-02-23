#' Compute IBR Composite Index
#' @param parameters List of parameter values
#' @return IBR result
#' @export
ibr_composite <- function(parameters) {
  weights <- list(VCA=0.20, MDI=0.15, PTS=0.12, HFI=0.11, BNC=0.10,
                  SGH=0.09, AES=0.08, TMI=0.08, RRC=0.07)
  
  score <- 0
  for (name in names(weights)) {
    if (name %in% names(parameters)) {
      score <- score + parameters[[name]] * weights[[name]]
    }
  }
  
  if (score > 0.88) cls <- "PRISTINE"
  else if (score > 0.75) cls <- "FUNCTIONAL"
  else if (score > 0.60) cls <- "IMPAIRED"
  else if (score > 0.45) cls <- "DEGRADED"
  else cls <- "COLLAPSED"
  
  structure(list(score=score, class=cls), class="ibr")
}

#' @export
print.ibr <- function(x, ...) {
  cat("IBR Score:", round(x$score, 3), "\n")
  cat("Class:", x$class, "\n")
}
