\name{bayesian_weights_complete}
\alias{bayesian_weights_complete}
\title{Bayesian Weight Estimation}
\description{
  Estimate IBR parameter weights using Bayesian methods
}
\usage{
bayesian_weights_complete(data, iter = 2000)
}
\arguments{
  \item{data}{Data frame with parameter columns}
  \item{iter}{Number of MCMC iterations}
}
\value{
  List with weight estimates and diagnostics
}
\examples{
\dontrun{
data <- data.frame(VCA=runif(100), MDI=runif(100), IBR=runif(100))
weights <- bayesian_weights_complete(data)
}
}
