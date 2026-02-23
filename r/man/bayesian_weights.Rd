\name{bayesian_weights}
\alias{bayesian_weights}
\title{Bayesian Weights}
\description{
  Estimates Bayesian weights for IBR parameters.
}
\usage{
bayesian_weights(data, iter = 2000)
}
\arguments{
  \item{data}{Data frame with parameters and IBR}
  \item{iter}{Number of MCMC iterations}
}
\value{
  List with weight estimates.
}
\examples{
\dontrun{
data <- data.frame(VCA = runif(100), MDI = runif(100), IBR = runif(100))
weights <- bayesian_weights(data)
print(weights)
}
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
