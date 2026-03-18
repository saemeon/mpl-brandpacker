# Copyright (c) Simon Niederberger.
# Distributed under the terms of the MIT License.

from __future__ import annotations

import base64
import io
from typing import Callable

import dash
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html

plt.switch_backend("agg")


def mpl_export_button(
    graph_id: str,
    renderer: Callable | None = None,
) -> html.Div:
    """Add a matplotlib export wizard button for a dcc.Graph.

    Parameters
    ----------
    graph_id :
        The ``id`` of the ``dcc.Graph`` component in the layout.
    renderer :
        Optional callable ``(fig_data: dict) -> matplotlib.figure.Figure``.
        If omitted, snapshot mode is used.

    Returns
    -------
    html.Div
        A component containing the trigger button and the self-contained modal.
        Place it anywhere in the layout.
    """
    modal_id = f"_s5ndt_modal_{graph_id}"
    store_id = f"_s5ndt_store_{graph_id}"
    close_id = f"_s5ndt_close_{graph_id}"
    generate_id = f"_s5ndt_generate_{graph_id}"
    download_id = f"_s5ndt_download_{graph_id}"
    preview_id = f"_s5ndt_preview_{graph_id}"
    title_id = f"_s5ndt_title_{graph_id}"
    suptitle_id = f"_s5ndt_suptitle_{graph_id}"
    trigger_id = f"_s5ndt_trigger_{graph_id}"

    modal = html.Div(
        id=modal_id,
        style={"display": "none"},
        children=[
            # overlay (purely decorative, does not capture clicks)
            html.Div(
                style={
                    "position": "fixed",
                    "inset": "0",
                    "background": "rgba(0,0,0,0.4)",
                    "zIndex": 1000,
                    "pointerEvents": "none",
                }
            ),
            # dialog
            html.Div(
                style={
                    "position": "fixed",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                    "background": "white",
                    "padding": "24px",
                    "zIndex": 1001,
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "16px",
                    "minWidth": "600px",
                },
                children=[
                    # header
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between"},
                        children=[
                            html.Strong("Export as matplotlib figure"),
                            html.Button("✕", id=close_id),
                        ],
                    ),
                    # body: two columns
                    html.Div(
                        style={"display": "flex", "gap": "24px"},
                        children=[
                            # left: inputs
                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                    "minWidth": "160px",
                                },
                                children=[
                                    html.Label("Suptitle"),
                                    dcc.Input(
                                        id=suptitle_id, type="text", placeholder=""
                                    ),
                                    html.Label("Title"),
                                    dcc.Input(id=title_id, type="text", placeholder=""),
                                    html.Button("Generate", id=generate_id),
                                ],
                            ),
                            # right: preview
                            html.Div(
                                children=[
                                    html.Img(
                                        id=preview_id, style={"maxWidth": "400px"}
                                    ),
                                ]
                            ),
                        ],
                    ),
                    # footer
                    dcc.Download(id=download_id),
                    html.Button("Download PNG", id=f"{download_id}_btn"),
                ],
            ),
        ],
    )

    store = dcc.Store(id=store_id, data=False)

    # --- callbacks ---

    @dash.callback(
        Output(store_id, "data"),
        Input(trigger_id, "n_clicks"),
        Input(close_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_store(open_clicks, close_clicks):
        from dash import ctx

        return ctx.triggered_id == trigger_id

    @dash.callback(
        Output(modal_id, "style"),
        Input(store_id, "data"),
    )
    def update_modal_visibility(is_open):
        return {"display": "block"} if is_open else {"display": "none"}

    @dash.callback(
        Output(preview_id, "src"),
        Input(generate_id, "n_clicks"),
        State(graph_id, "figure"),
        State(suptitle_id, "value"),
        State(title_id, "value"),
        prevent_initial_call=True,
    )
    def generate_preview(n_clicks, figure, suptitle, title):
        fig = _render_figure(figure, renderer, suptitle, title)
        return _fig_to_src(fig)

    @dash.callback(
        Output(download_id, "data"),
        Input(f"{download_id}_btn", "n_clicks"),
        State(graph_id, "figure"),
        State(suptitle_id, "value"),
        State(title_id, "value"),
        prevent_initial_call=True,
    )
    def download_figure(n_clicks, figure, suptitle, title):
        fig = _render_figure(figure, renderer, suptitle, title)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return dcc.send_bytes(buf.read(), "figure.png")

    return html.Div([html.Button("Export", id=trigger_id), store, modal])


def _render_figure(figure, renderer, suptitle, title):
    if renderer is not None:
        fig = renderer(figure)
    else:
        fig = _snapshot_render(figure)

    ax = fig.axes[0] if fig.axes else fig.add_subplot(111)
    if title:
        ax.set_title(title)
    if suptitle:
        fig.suptitle(suptitle)

    return fig


def _snapshot_render(figure):
    plotly_fig = go.Figure(figure)
    img_bytes = plotly_fig.to_image(format="png")
    img = plt.imread(io.BytesIO(img_bytes))
    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.axis("off")
    return fig


def _fig_to_src(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"
