\name{analyze_timeseries}
\alias{analyze_timeseries}
\title{Analyze Time Series}
\description{
  Performs comprehensive time series analysis.
}
\usage{
analyze_timeseries(x, frequency = 1)
}
\arguments{
  \item{x}{Time series vector}
  \item{frequency}{Seasonal frequency}
}
\value{
  List with trend, seasonality, and autocorrelation.
}
\examples{
x <- cumsum(rnorm(120))
result <- analyze_timeseries(x, frequency = 12)
print(result)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
