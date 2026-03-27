"""Branded drop-in for ``matplotlib.pyplot``.

Intercepts three entry points — ``figure()``, ``gcf()``, ``gca()`` — to
auto-patch every new Figure and Axes through the hooks set via
:func:`mpl_brandpacker.configure`. All other pyplot functions (``subplots()``, ``subplot_mosaic()``, ``axes()``,
``show()``, etc.) are not modified but work correctly because they internally
call ``figure()`` or ``gcf()`` — which are patched — so the brand hooks
propagate automatically through the entire pyplot API.

Usage::

    import mpl_brandpacker
    mpl_brandpacker.configure(figure_cls=..., axes_cls=...)

    import mpl_brandpacker.pyplot as plt
    fig, ax = plt.subplots()  # both branded

Extending pyplot
-----------------

Your brand's ``pyplot.py`` can add pyplot-level shortcuts for brand methods,
mirroring matplotlib's ``plt.title()`` pattern::

    # my_brand/pyplot.py
    from mpl_brandpacker.pyplot import *  # noqa
    from mpl_brandpacker.pyplot import gcf

    def title(title, **kw):     gcf().set_title(title, **kw)
    def subtitle(sub, **kw):    gcf().set_subtitle(sub, **kw)
    def sources(src, **kw):     gcf().set_sources(src, **kw)
    def footnote(note, **kw):   gcf().set_footnote(note, **kw)

See the template package for a complete example.
"""

from __future__ import annotations

import importlib
import sys

import matplotlib.pyplot
from matplotlib.pyplot import *  # noqa

from mpl_brandpacker._config import get_make_ax, get_make_fig

_spec_plt = importlib.util.find_spec(
    "matplotlib"
)  # ty:ignore[possibly-missing-submodule]
_bp_matplotlib = importlib.util.module_from_spec(_spec_plt)  # type: ignore[arg-type]  # ty:ignore[possibly-missing-submodule]
_spec_plt.loader.exec_module(_bp_matplotlib)  # type: ignore[union-attr]
sys.modules["_bp_matplotlib"] = _bp_matplotlib

import _bp_matplotlib.pyplot  # noqa  # type: ignore[import-not-found]  # ty:ignore[unresolved-import]


def _patched_gcf():
    """Get the current figure, patch it."""
    fig = matplotlib.pyplot.gcf()  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    return get_make_fig()(fig)


_bp_matplotlib.pyplot.gcf = _patched_gcf  # type: ignore[attr-defined]


def _patched_gca(**kwargs):
    """Get the current axes, patch it."""
    ax = matplotlib.pyplot.gca(**kwargs)  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    return get_make_ax()(ax)


_bp_matplotlib.pyplot.gca = _patched_gca  # type: ignore[attr-defined]


def _patched_figure(*args, **kwargs):
    """Create a new figure, patch it."""
    fig = matplotlib.pyplot.figure(*args, **kwargs)  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
    return get_make_fig()(fig)


_bp_matplotlib.pyplot.figure = _patched_figure  # type: ignore[attr-defined]


# Import all objects from _bp_matplotlib.pyplot AFTER the overrides
from _bp_matplotlib.pyplot import *  # noqa  # type: ignore[import-not-found]  # ty:ignore[unresolved-import]
