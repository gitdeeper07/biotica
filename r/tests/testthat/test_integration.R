test_that("Python integration functions exist", {
  expect_true(exists("setup_python_integration"))
  expect_true(exists("python_ibr"))
})

test_that("Utility functions work", {
  expect_equal(normalize(5, 0, 10), 0.5)
  expect_equal(clip(1.5, 0, 1), 1)
  expect_equal(clip(-0.5, 0, 1), 0)
  expect_equal(weighted_sum(c(1,2), c(0.5,0.5)), 1.5)
})
