# shinycorpframe demo — run with:
#   cd r-packages/shinycorpframe
#   /usr/local/bin/Rscript examples/corporate_demo.R

library(shiny)
library(plotly)

devtools::load_all("../shinycapture")
devtools::load_all(".")

ui <- fluidPage(
  tags$head(tags$script(
    src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.0/html2canvas.min.js"
  )),

  titlePanel("shinycorpframe — Corporate Chart Export"),

  plotlyOutput("revenue_chart", width = "700px", height = "400px"),
  br(),

  h4("One-click corporate export"),
  actionButton("export_btn", "Export with Corporate Frame"),
  br(), br(),
  uiOutput("framed_preview"),
  uiOutput("download_ui"),
)

server <- function(input, output, session) {

  output$revenue_chart <- renderPlotly({
    plot_ly(
      x = c("Q1", "Q2", "Q3", "Q4"),
      y = c(120, 145, 132, 178),
      type = "bar",
      name = "2025",
      marker = list(color = "#1a1a2e")
    ) %>%
      add_trace(
        y = c(135, 160, 148, 195),
        name = "2026",
        marker = list(color = "#e94560")
      ) %>%
      layout(
        title = "Quarterly Revenue (CHF M)",
        xaxis = list(title = ""),
        yaxis = list(title = "Revenue (CHF M)"),
        barmode = "group"
      )
  })

  framed_bytes <- reactiveVal(NULL)

  observeEvent(input$export_btn, {
    capture_corporate(
      "revenue_chart",
      title = "Quarterly Revenue",
      subtitle = "Comparison 2025 vs 2026, all regions",
      footnotes = "Preliminary figures, subject to audit",
      sources = "Source: Internal ERP, March 2026",
      strip_title = TRUE,
      width = 1200,
      height = 800,
    )
  })

  # When the raw capture comes back, it triggers the Python postprocessor
  # via capture_corporate's internal observer.
  # We watch for the framed result:
  observeEvent(input[[".corpframe.revenue_chart_ready"]], {
    bytes <- session$userData[[".corpframe.revenue_chart"]]
    if (!is.null(bytes)) {
      framed_bytes(bytes)

      # Show preview
      b64 <- paste0(
        "data:image/png;base64,",
        jsonlite::base64_enc(bytes)
      )
      output$framed_preview <- renderUI({
        tagList(
          h4("Preview:"),
          tags$img(src = b64, style = "max-width:700px; border:1px solid #ccc;")
        )
      })

      # Show download button
      output$download_ui <- renderUI({
        downloadButton("download_framed", "Download Framed Chart")
      })
    }
  })

  output$download_framed <- downloadHandler(
    filename = function() "revenue_corporate.png",
    content = function(file) {
      writeBin(framed_bytes(), file)
    }
  )
}

shinyApp(ui, server)
