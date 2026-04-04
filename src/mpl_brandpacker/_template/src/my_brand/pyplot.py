"""Branded pyplot — drop-in replacement for matplotlib.pyplot.

Usage::

    import my_brand.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.set_xlabel("Quarter")

    plt.title("Q4 Revenue")
    plt.sources("Bloomberg")
    plt.show()
"""

from __future__ import annotations

from mpl_brandpacker.pyplot import *  # noqa: F401,F403
from mpl_brandpacker.pyplot import gcf

# ---------------------------------------------------------------------------
# pyplot-level convenience functions for brand methods.
# Mirrors matplotlib's plt.title() / plt.xlabel() pattern.
# ---------------------------------------------------------------------------


def title(title: str, **kwargs):
    """Set title on the current figure (branded header)."""
    return gcf().set_title(title, **kwargs)


def subtitle(subtitle: str, **kwargs):
    """Set subtitle on the current figure (branded header)."""
    return gcf().set_subtitle(subtitle, **kwargs)


def sources(sources: str, **kwargs):
    """Set sources on the current figure (branded footer)."""
    return gcf().set_sources(sources, **kwargs)


def footnote(footnote: str, **kwargs):
    """Set footnote on the current figure (branded footer)."""
    return gcf().set_footnote(footnote, **kwargs)
