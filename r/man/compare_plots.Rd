\name{compare_plots}
\alias{compare_plots}
\title{Compare Plots}
\description{
  Creates a barplot comparing IBR scores across multiple plots.
}
\usage{
compare_plots(plot_data, main = "IBR Score Comparison")
}
\arguments{
  \item{plot_data}{Data frame with plot IDs and IBR scores}
  \item{main}{Plot title}
}
\value{
  None, creates a plot.
}
\examples{
plots <- data.frame(id = 1:10, ibr = runif(10))
compare_plots(plots)
}
\author{
Samir Baladi \email{gitdeeper@gmail.com}
}
