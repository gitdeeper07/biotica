test_that("IBR computation works", {
  params <- list(VCA=0.85, MDI=0.78)
  res <- ibr_composite(params)
  expect_true(res$score > 0)
})

test_that("Validation works", {
  expect_true(validate_parameters(list(VCA=0.5)))
  expect_false(validate_parameters(list(VCA=1.5)))
})
