#' Integration with Python BIOTICA
#'
#' @param python_path Path to Python executable
#' @return Logical indicating success
#' @export
#'
#' @examples
#' \dontrun{
#' setup_python_integration()
#' }

setup_python_integration <- function(python_path = NULL) {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    message("reticulate package not installed. Install with: install.packages('reticulate')")
    return(FALSE)
  }
  
  if (!is.null(python_path)) {
    reticulate::use_python(python_path)
  }
  
  # Check if biotica Python package is available
  py_available <- reticulate::py_module_available("biotica")
  
  if (py_available) {
    message("Python BIOTICA package found")
    return(TRUE)
  } else {
    message("Python BIOTICA package not found")
    return(FALSE)
  }
}

#' Call Python BIOTICA from R
#'
#' @param params List of parameters
#' @return IBR result from Python
#' @export
#'
#' @examples
#' \dontrun{
#' params <- list(VCA=0.85, MDI=0.78)
#' python_ibr(params)
#' }

python_ibr <- function(params) {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    stop("reticulate package required")
  }
  
  biotica <- reticulate::import("biotica")
  core <- biotica$BIOTICACore()
  result <- core$compute_ibr(params)
  
  return(result)
}
