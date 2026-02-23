#' Validate Parameters
#' @param params List of parameters
#' @return Logical
#' @export
validate_parameters <- function(params) {
  for (val in params) {
    if (!is.numeric(val) || val < 0 || val > 1) {
      return(FALSE)
    }
  }
  return(TRUE)
}
