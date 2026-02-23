#' Test complete BIOTICA workflow
#' 
#' This test runs a complete workflow to ensure all functions work together

test_that("Complete workflow runs without errors", {
  skip_on_cran()
  
  # Generate test data
  set.seed(123)
  n <- 50
  
  test_data <- data.frame(
    VCA = runif(n, 0.5, 0.9),
    MDI = runif(n, 0.5, 0.9),
    PTS = runif(n, 0.5, 0.9),
    HFI = runif(n, 0.5, 0.9),
    BNC = runif(n, 0.5, 0.9),
    SGH = runif(n, 0.5, 0.9),
    AES = runif(n, 0.5, 0.9),
    TMI = runif(n, 0.5, 0.9),
    RRC = runif(n, 0.5, 0.9)
  )
  
  # Step 1: Compute IBR for each row
  ibr_scores <- apply(test_data, 1, function(row) {
    params <- as.list(row)
    result <- ibr_composite(params)
    return(result$score)
  })
  
  expect_length(ibr_scores, n)
  expect_true(all(ibr_scores > 0))
  expect_true(all(ibr_scores < 1))
  
  # Step 2: Add IBR to data
  test_data$IBR <- ibr_scores
  
  # Step 3: Compute statistics
  stats <- ecosystem_stats(test_data)
  expect_s3_class(stats, "ecosystem_stats")
  
  # Step 4: Compute correlations
  corr <- parameter_correlation(test_data)
  expect_s3_class(corr, "parameter_correlation")
  
  # Step 5: Bayesian weights
  weights <- bayesian_weights_complete(test_data)
  expect_s3_class(weights, "bayesian_weights_complete")
  
  # Step 6: Validate parameters
  valid <- validate_parameters(as.list(test_data[1, 1:9]))
  expect_true(valid)
  
  cat("\n✓ Complete workflow test passed\n")
})
