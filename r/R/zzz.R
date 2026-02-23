#' Package load hook
#'
.onLoad <- function(libname, pkgname) {

Nothing needed

}

.onAttach <- function(libname, pkgname) {
msg <- paste("BIOTICA R Package v1.0.0")
packageStartupMessage(msg)
}
