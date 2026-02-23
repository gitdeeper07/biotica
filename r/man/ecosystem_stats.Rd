\name{ecosystem_stats}
\alias{ecosystem_stats}
\title{Ecosystem Statistics}
\description{
  Computes descriptive statistics for ecosystem parameters.
}
\usage{
ecosystem_stats(data)
}
\arguments{
  \item{data}{Data frame with parameter columns}
}
\value{
  List of statistics for each parameter.
}
\examples{
data <- data.frame(VCA = runif(50), MDI = runif(50))
stats <- ecosystem_stats(data)
print(stats)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
