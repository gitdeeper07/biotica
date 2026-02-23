\name{ibr_composite}
\alias{ibr_composite}
\title{Compute IBR Composite Index}
\description{
  Computes the Integrated Biotic Resilience (IBR) index from parameter values.
}
\usage{
ibr_composite(parameters)
}
\arguments{
  \item{parameters}{A named list of parameter values (VCA, MDI, PTS, etc.)}
}
\value{
  An object of class "ibr" containing:
  \item{score}{The IBR score (0-1)}
  \item{class}{The resilience class (PRISTINE, FUNCTIONAL, IMPAIRED, DEGRADED, COLLAPSED)}
}
\examples{
params <- list(VCA = 0.85, MDI = 0.78, PTS = 0.82)
result <- ibr_composite(params)
print(result)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
