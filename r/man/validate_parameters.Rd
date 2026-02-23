\name{validate_parameters}
\alias{validate_parameters}
\title{Validate Parameter Values}
\description{
  Checks if parameter values are valid (numeric and between 0 and 1).
}
\usage{
validate_parameters(params)
}
\arguments{
  \item{params}{A list of parameter values}
}
\value{
  Logical: TRUE if all parameters are valid, FALSE otherwise.
}
\examples{
validate_parameters(list(VCA = 0.85, MDI = 0.78))  # TRUE
validate_parameters(list(VCA = 1.5, MDI = -0.2))   # FALSE
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
