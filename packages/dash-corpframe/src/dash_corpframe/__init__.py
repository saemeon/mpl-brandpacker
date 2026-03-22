# Copyright (c) Simon Niederberger.
# Distributed under the terms of the MIT License.

"""dash-corpframe — one-click corporate-framed chart capture for Dash."""

from dash_corpframe.corporate_frame import corporate_renderer
from dash_corpframe.capture import corporate_capture_graph

__all__ = [
    "corporate_capture_graph",
    "corporate_renderer",
]
