test_that("Tipping point detection works", {
  x <- cumsum(rnorm(100))
  result <- tipping_points(x)
  
  expect_s3_class(result, "tipping_result")
  expect_true(result$warning_level >= 0)
  expect_true(result$warning_level <= 3)
  expect_true(abs(result$variance_trend) <= 1)
})

test_that("Tipping point handles small windows", {
  x <- rnorm(10)
  result <- tipping_points(x, window = 5)
  expect_s3_class(result, "tipping_result")
})
