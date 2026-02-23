\name{parameter_correlation}
\alias{parameter_correlation}
\title{Parameter Correlation}
\description{
  Computes correlation matrix for ecosystem parameters.
}
\usage{
parameter_correlation(data, method = "pearson")
}
\arguments{
  \item{data}{Data frame with parameter columns}
  \item{method}{Correlation method ("pearson", "spearman", "kendall")}
}
\value{
  Correlation matrix.
}
\examples{
data <- data.frame(VCA = runif(50), MDI = runif(50), PTS = runif(50))
corr <- parameter_correlation(data)
print(corr)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
