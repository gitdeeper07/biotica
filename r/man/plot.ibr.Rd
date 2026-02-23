\name{plot.ibr}
\alias{plot.ibr}
\title{Plot IBR Result}
\description{
  Plot method for IBR result objects.
}
\usage{
\method{plot}{ibr}(x, ...)
}
\arguments{
  \item{x}{An object of class "ibr"}
  \item{...}{Additional plotting arguments}
}
\value{
  None, creates a barplot.
}
\examples{
params <- list(VCA = 0.85, MDI = 0.78, PTS = 0.82)
result <- ibr_composite(params)
plot(result)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
