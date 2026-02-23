test_that("Parameter validation works", {
  expect_true(validate_parameters(list(VCA = 0.5)))
  expect_false(validate_parameters(list(VCA = 1.5)))
  expect_false(validate_parameters(list(VCA = "a")))
})

test_that("Validation messages are attached", {
  result <- validate_parameters(list(VCA = 1.5))
  messages <- attr(result, "messages")
  expect_true(length(messages) > 0)
})
