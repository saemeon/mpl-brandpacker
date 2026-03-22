# Copyright (c) Simon Niederberger.
# Distributed under the terms of the MIT License.

#' Capture a Plotly chart with corporate framing
#'
#' Triggers a browser capture of a Plotly chart, then applies the corporate
#' design frame (header with title/subtitle, footer with footnotes/sources)
#' via a Python/matplotlib subprocess.
#'
#' @param id The output ID of the \code{plotlyOutput} to capture.
#' @param title Header title.
#' @param subtitle Header subtitle.
#' @param footnotes Footer footnotes (left-aligned).
#' @param sources Footer sources (right-aligned).
#' @param strip_title Remove the Plotly figure title before capture.
#' @param strip_legend Remove the legend before capture.
#' @param width Capture width in pixels (NULL = displayed size).
#' @param height Capture height in pixels (NULL = displayed size).
#' @param dpi Output resolution for the framed image.
#' @param python Path to Python executable (NULL for auto-detect).
#' @param input_id Shiny input ID for the final framed result.
#'   Defaults to \code{".corpframe.<id>"}.
#' @param session Shiny session.
#' @return Invisibly, the \code{input_id} for the framed result.
#'
#' @details
#' The capture flow:
#' \enumerate{
#'   \item Browser captures the Plotly chart via shinycapture
#'   \item R receives the base64 PNG
#'   \item R calls Python subprocess with corporate_frame.py
#'   \item Python adds header (title, subtitle) + footer (footnotes, sources)
#'   \item R receives framed PNG bytes
#'   \item Result available at \code{input[[input_id]]} as raw bytes
#' }
#'
#' @examples
#' \dontrun{
#' server <- function(input, output, session) {
#'   output$my_plot <- plotly::renderPlotly({ ... })
#'
#'   observeEvent(input$export_btn, {
#'     capture_corporate("my_plot",
#'       title = "Q4 Revenue",
#'       subtitle = "By region, 2026",
#'       footnotes = "Internal data, preliminary",
#'       sources = "Source: Bloomberg"
#'     )
#'   })
#'
#'   # Framed result arrives here
#'   observeEvent(input[[".corpframe.my_plot"]], {
#'     bytes <- input[[".corpframe.my_plot"]]
#'     # Display, download, or save
#'   })
#' }
#' }
#' @export
capture_corporate <- function(id,
                              title = "",
                              subtitle = "",
                              footnotes = "",
                              sources = "",
                              strip_title = TRUE,
                              strip_legend = FALSE,
                              width = 1200L,
                              height = 800L,
                              dpi = 300L,
                              python = NULL,
                              input_id = NULL,
                              session = shiny::getDefaultReactiveDomain()) {
  if (is.null(input_id)) {
    input_id <- paste0(".corpframe.", id)
  }

  # Intermediate input ID for the raw capture
  raw_id <- paste0(".corpframe.raw.", id)

  # Step 1: capture via shinycapture
  shinycapture::capture_plotly(
    id,
    strategy = shinycapture::plotly_strategy(
      strip_title = strip_title,
      strip_legend = strip_legend,
      width = width,
      height = height
    ),
    input_id = raw_id,
    session = session
  )

  # Step 2: when raw capture arrives, apply corporate frame via Python
  shiny::observeEvent(
    session$input[[raw_id]],
    {
      b64 <- session$input[[raw_id]]
      raw_bytes <- shinycapture::base64_decode(b64)

      # Call Python postprocessor
      framed_bytes <- .apply_frame(
        raw_bytes,
        title = title,
        subtitle = subtitle,
        footnotes = footnotes,
        sources = sources,
        dpi = dpi,
        python = python
      )

      # Make available as reactive value
      session$userData[[input_id]] <- framed_bytes

      # Trigger observers by setting a custom input
      session$sendCustomMessage(
        "shinycorpframe-result",
        list(input_id = input_id)
      )
    },
    once = TRUE,
    ignoreInit = TRUE
  )

  invisible(input_id)
}


#' One-click corporate capture button
#'
#' Creates an action button that, when clicked, captures and frames the chart.
#' The framed result is displayed as a preview and offered as a download.
#'
#' @param plot_id The output ID of the plotlyOutput.
#' @param button_id Unique ID for the capture button.
#' @param title,subtitle,footnotes,sources Corporate frame text.
#' @param strip_title,strip_legend Pre-capture stripping.
#' @param width,height Capture resolution in pixels.
#' @param download_filename Filename for the download button.
#' @return A tagList with the capture button. Call
#'   \code{corporate_frame_server()} in your server function.
#' @export
corporate_frame_button <- function(plot_id,
                                   button_id = paste0("corpframe_", plot_id),
                                   title = "",
                                   subtitle = "",
                                   footnotes = "",
                                   sources = "",
                                   strip_title = TRUE,
                                   strip_legend = FALSE,
                                   width = 1200L,
                                   height = 800L,
                                   download_filename = "chart.png") {
  shiny::tagList(
    shinycapture::shinycapture_deps(),
    shiny::actionButton(button_id, "Export (Corporate)"),
    shiny::uiOutput(paste0(button_id, "_preview")),
    shiny::tags$script(shiny::HTML(sprintf("
      Shiny.addCustomMessageHandler('shinycorpframe-result', function(msg) {
        Shiny.setInputValue(msg.input_id + '_ready', true, {priority: 'event'});
      });
    ")))
  )
}
