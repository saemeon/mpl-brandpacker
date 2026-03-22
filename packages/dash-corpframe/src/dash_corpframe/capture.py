# Copyright (c) Simon Niederberger.
# Distributed under the terms of the MIT License.

"""One-click corporate capture for Dash — wraps dash-capture with the
corporate renderer pre-configured."""

from __future__ import annotations

from typing import Any

from dash import dcc, html

from dash_capture import capture_graph, plotly_strategy
from dash_corpframe.corporate_frame import corporate_renderer


def corporate_capture_graph(
    graph: str | dcc.Graph,
    trigger: str | Any = "Export (Corporate)",
    title: str = "",
    subtitle: str = "",
    footnotes: str = "",
    sources: str = "",
    strip_title: bool = True,
    strip_legend: bool = False,
    strip_annotations: bool = False,
    strip_margin: bool = False,
    filename: str = "chart_corporate.png",
    styles: dict | None = None,
    class_names: dict | None = None,
    field_components: Any = "dcc",
) -> html.Div:
    """One-click corporate capture button for a ``dcc.Graph``.

    Combines ``capture_graph`` with the corporate frame renderer.
    The wizard shows fields for title, subtitle, footnotes, and sources
    — pre-filled with the values passed here.

    Parameters
    ----------
    graph :
        The ``dcc.Graph`` component or its string ``id``.
    trigger :
        Button label or custom component.
    title :
        Default header title.
    subtitle :
        Default header subtitle.
    footnotes :
        Default footer footnotes.
    sources :
        Default footer sources.
    strip_title :
        Remove the Plotly title before capture (default True — the
        corporate header replaces it).
    filename :
        Download filename.

    Example::

        app.layout = html.Div([
            dcc.Graph(id="revenue", figure=fig),
            corporate_capture_graph(
                "revenue",
                title="Q4 Revenue",
                subtitle="By region, 2026",
                sources="Source: Bloomberg",
            ),
        ])
    """
    # Pre-fill the renderer fields with the provided defaults via field_specs
    from dash_fn_forms import Field

    field_specs = {}
    if title:
        field_specs["title"] = Field(default=title, persist=True)
    if subtitle:
        field_specs["subtitle"] = Field(default=subtitle, persist=True)
    if footnotes:
        field_specs["footnotes"] = Field(default=footnotes, persist=True)
    if sources:
        field_specs["sources"] = Field(default=sources, persist=True)

    return capture_graph(
        graph,
        renderer=corporate_renderer,
        trigger=trigger,
        strip_title=strip_title,
        strip_legend=strip_legend,
        strip_annotations=strip_annotations,
        strip_margin=strip_margin,
        filename=filename,
        autogenerate=False,
        persist=True,
        styles=styles,
        class_names=class_names,
        field_specs=field_specs or None,
        field_components=field_components,
    )
