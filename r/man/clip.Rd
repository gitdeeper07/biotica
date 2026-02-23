\name{clip}
\alias{clip}
\title{Clip a Value}
\description{
  Clips a value to a specified range.
}
\usage{
clip(x, min_val = 0, max_val = 1)
}
\arguments{
  \item{x}{Value to clip}
  \item{min_val}{Minimum allowed value}
  \item{max_val}{Maximum allowed value}
}
\value{
  Clipped value.
}
\examples{
clip(1.5, 0, 1)  # Returns 1
clip(-0.5, 0, 1) # Returns 0
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
