test_that("Bayesian weights complete works", {
  skip_if_not_installed("stats")
  
  data <- data.frame(
    VCA = runif(50),
    MDI = runif(50),
    IBR = runif(50)
  )
  
  result <- bayesian_weights_complete(data)
  expect_s3_class(result, "bayesian_weights_complete")
  expect_equal(length(result$weights), 2)
  expect_equal(length(result$uncertainty), 2)
})

test_that("Time series analysis works", {
  x <- cumsum(rnorm(120))
  result <- analyze_timeseries(x, frequency = 12)
  expect_s3_class(result, "timeseries_analysis")
  expect_true(result$length == 120)
  expect_true(!is.null(result$mean))
})

test_that("Compare plots works", {
  plots <- data.frame(
    id = 1:10,
    ibr = runif(10)
  )
  
  # Just test that it runs without error
  expect_error(compare_plots(plots), NA)
})

test_that("Ecosystem stats works", {
  data <- data.frame(
    VCA = runif(100),
    MDI = runif(100),
    PTS = runif(100)
  )
  
  result <- ecosystem_stats(data)
  expect_s3_class(result, "ecosystem_stats")
  expect_equal(length(result), 3)
  expect_true(!is.null(result$VCA$mean))
})

test_that("Parameter correlation works", {
  data <- data.frame(
    VCA = runif(100),
    MDI = runif(100),
    IBR = runif(100)
  )
  
  result <- parameter_correlation(data)
  expect_s3_class(result, "parameter_correlation")
  expect_equal(dim(result$correlation), c(3, 3))
  expect_equal(dim(result$p_value), c(3, 3))
})
