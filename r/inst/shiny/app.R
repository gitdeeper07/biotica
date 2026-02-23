#' Simple Shiny App for BIOTICA
#' 
#' Interactive IBR calculator
#' Run with: shiny::runApp(system.file("shiny", package = "biotica"))

library(shiny)
library(biotica)

ui <- fluidPage(
  titlePanel("BIOTICA IBR Calculator"),
  
  sidebarLayout(
    sidebarPanel(
      h4("Input Parameters"),
      sliderInput("vca", "VCA:", min = 0, max = 1, value = 0.8, step = 0.01),
      sliderInput("mdi", "MDI:", min = 0, max = 1, value = 0.8, step = 0.01),
      sliderInput("pts", "PTS:", min = 0, max = 1, value = 0.8, step = 0.01),
      sliderInput("hfi", "HFI:", min = 0, max = 1, value = 0.8, step = 0.01),
      sliderInput("bnc", "BNC:", min = 0, max = 1, value = 0.8, step = 0.01),
      actionButton("compute", "Compute IBR", class = "btn-primary")
    ),
    
    mainPanel(
      h4("Results"),
      verbatimTextOutput("result"),
      plotOutput("contributions")
    )
  )
)

server <- function(input, output) {
  
  ibr_result <- eventReactive(input$compute, {
    params <- list(
      VCA = input$vca,
      MDI = input$mdi,
      PTS = input$pts,
      HFI = input$hfi,
      BNC = input$bnc,
      SGH = 0.7,  # Default values for other params
      AES = 0.7,
      TMI = 0.7,
      RRC = 0.7
    )
    ibr_composite(params)
  })
  
  output$result <- renderPrint({
    result <- ibr_result()
    cat("IBR Score:", round(result$score, 3), "\n")
    cat("Classification:", result$classification, "\n")
  })
  
  output$contributions <- renderPlot({
    result <- ibr_result()
    contributions <- unlist(result$contributions)
    barplot(contributions,
            main = "Parameter Contributions",
            xlab = "Parameter",
            ylab = "Contribution",
            col = "steelblue",
            las = 2)
  })
}

shinyApp(ui = ui, server = server)
