"""Type stubs for my_brand.pyplot — gives IDE autocompletion for brand methods."""

from collections.abc import Sequence
from typing import Any, Literal, overload

import numpy as np
from matplotlib.pyplot import *  # noqa: F403

from my_brand.axes import MyAxes
from my_brand.figure import MyFigure

# -- subplots overloads (mirrors matplotlib's pattern) ----------------------

@overload
def subplots(
    nrows: Literal[1] = ...,
    ncols: Literal[1] = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[True] = ...,
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw: Any,
) -> tuple[MyFigure, MyAxes]: ...
@overload
def subplots(
    nrows: int = ...,
    ncols: int = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[False],
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw: Any,
) -> tuple[MyFigure, np.ndarray]: ...
@overload
def subplots(
    nrows: int = ...,
    ncols: int = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: bool = ...,
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw: Any,
) -> tuple[MyFigure, Any]: ...

# -- single-return functions ------------------------------------------------

def figure(num: int | str | None = ..., **kwargs: Any) -> MyFigure: ...
def gcf() -> MyFigure: ...
def gca(**kwargs: Any) -> MyAxes: ...

# -- brand convenience functions --------------------------------------------

def title(title: str, **kwargs: Any) -> None: ...
def subtitle(subtitle: str, **kwargs: Any) -> None: ...
def sources(sources: str, **kwargs: Any) -> None: ...
def footnote(footnote: str, **kwargs: Any) -> None: ...
