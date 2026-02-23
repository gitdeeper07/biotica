\name{tipping_points}
\alias{tipping_points}
\title{Detect Ecosystem Tipping Points}
\description{
  Detects early warning signals of critical transitions in time series data.
}
\usage{
tipping_points(x)
}
\arguments{
  \item{x}{A numeric vector time series}
}
\value{
  An object of class "tipping" containing:
  \item{variance_trend}{Kendall trend of rolling variance}
  \item{warning}{Warning status ("WARNING" or "OK")}
}
\examples{
x <- cumsum(rnorm(100))
result <- tipping_points(x)
print(result)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
