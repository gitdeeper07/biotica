#' Enhanced Python Integration
#'
#' @return List of available Python functions
#' @export
#'
#' @examples
#' \dontrun{
#' check_python_biotica()
#' }

check_python_biotica <- function() {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    message("Install reticulate: install.packages('reticulate')")
    return(list(available = FALSE))
  }
  
  tryCatch({
    biotica <- reticulate::import("biotica", delay_load = TRUE)
    available <- TRUE
    version <- biotica$`__version__`
    functions <- c("BIOTICACore", "compute_ibr", "compute_vca")
    
    list(
      available = available,
      version = version,
      functions = functions
    )
  }, error = function(e) {
    list(
      available = FALSE,
      error = e$message
    )
  })
}

#' Convert R list to Python dict
#'
#' @param r_list R list
#' @return Python dictionary
#' @export
#'
#' @examples
#' \dontrun{
#' params <- list(VCA = 0.85, MDI = 0.78)
#' py_dict <- r_to_py_dict(params)
#' }

r_to_py_dict <- function(r_list) {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    stop("reticulate required")
  }
  reticulate::r_to_py(r_list)
}

#' Convert Python dict to R list
#'
#' @param py_dict Python dictionary
#' @return R list
#' @export
#'
#' @examples
#' \dontrun{
#' py_dict <- list(VCA = 0.85, MDI = 0.78)
#' r_list <- py_to_r_list(py_dict)
#' }

py_to_r_list <- function(py_dict) {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    stop("reticulate required")
  }
  reticulate::py_to_r(py_dict)
}
