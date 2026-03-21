# Copyright (c) Simon Niederberger.
# Distributed under the terms of the MIT License.

"""Implicit (Streamlit-style) convenience layer over :class:`~dash_fn_interact.Page`.

Inspired by ``matplotlib.pyplot``: a module-level singleton accumulates panels
in call order; :func:`run` renders everything — no ``Page`` object needed.

Usage::

    from dash_fn_interact.page import interact, add, run
    from dash import html

    add(html.H1("My App"))

    @interact
    def sine_wave(amplitude: float = 1.0, frequency: float = 2.0):
        ...

    run(debug=True)

For power users, :func:`get_page` exposes the current singleton (analogous to
``plt.gcf()``) and :func:`new_page` starts a fresh one (analogous to
``plt.figure()``).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dash_fn_interact._page import Page

_current: Page = Page()


# -- pyplot-style helpers --------------------------------------------------


def get_page() -> Page:
    """Return the current default :class:`~dash_fn_interact.Page` singleton.

    Analogous to ``matplotlib.pyplot.gcf()``.  Useful when you need to call
    a :class:`~dash_fn_interact.Page` method not exposed at module level.
    """
    return _current


def new_page(*, max_width: int = 960, manual: bool = False) -> Page:
    """Replace the default page with a fresh one and return it.

    Analogous to ``matplotlib.pyplot.figure()``.  Use this to start a new
    page in the same process (e.g. in tests or notebooks) without discarding
    the old one.

    Parameters
    ----------
    max_width, manual :
        Forwarded to :class:`~dash_fn_interact.Page`.
    """
    global _current
    _current = Page(max_width=max_width, manual=manual)
    return _current


# -- convenience wrappers --------------------------------------------------


def interact(
    fn: Callable | None = None,
    *,
    _manual: bool | None = None,
    **kwargs: Any,
) -> Any:
    """Add an interact panel to the default page.

    See :meth:`~dash_fn_interact.Page.interact` for full documentation.
    """
    return _current.interact(fn, _manual=_manual, **kwargs)


def add(*components: Any) -> None:
    """Append arbitrary Dash components to the default page.

    See :meth:`~dash_fn_interact.Page.add` for full documentation.
    """
    _current.add(*components)


def run(**kwargs: Any) -> None:
    """Build and run the default page as a Dash app.

    See :meth:`~dash_fn_interact.Page.run` for full documentation.
    """
    _current.run(**kwargs)
