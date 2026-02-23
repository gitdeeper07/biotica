\name{normalize}
\alias{normalize}
\title{Normalize a Value}
\description{
  Normalizes a value to a specified range.
}
\usage{
normalize(x, min_val = 0, max_val = 1)
}
\arguments{
  \item{x}{Value to normalize}
  \item{min_val}{Minimum of target range}
  \item{max_val}{Maximum of target range}
}
\value{
  Normalized value.
}
\examples{
normalize(5, 0, 10)  # Returns 0.5
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
