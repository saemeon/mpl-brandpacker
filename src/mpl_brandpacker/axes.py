"""Axes patching: base class + patcher.

``BrandAxes`` is a base class that brand implementations subclass.
Mark your custom axes methods with ``@brand_method`` and use
``patch_axes()`` to bind them onto plain Axes instances.

Example::

    from mpl_brandpacker.axes import BrandAxes, patch_axes
    from mpl_brandpacker import brand_method

    class MyAxes(BrandAxes):
        @brand_method
        def set_xlabel(self, label): ...

        @brand_method
        def legend(self, **kw): ...

        @brand_method
        def zeroline(self): ...

    patch_axes(ax, MyAxes, style_fn=set_my_style)
    ax.mpl.set_xlabel("raw")  # → original Axes.set_xlabel
"""

from __future__ import annotations

import functools

from matplotlib.axes import Axes

from mpl_brandpacker.patcher import MethodProxy, collect_brand_methods, patch_method


class BrandAxes(Axes):
    """Base class for brand Axes implementations.

    Subclass this and mark your brand methods with ``@brand_method``::

        class MyAxes(BrandAxes):
            @brand_method
            def set_xlabel(self, label, **kw): ...

            @brand_method
            def legend(self, **kw): ...

    After patching:

    - ``ax.set_xlabel("X")`` calls your method
    - ``ax.mpl.set_xlabel("X")`` calls original matplotlib Axes.set_xlabel
    """

    _brand_methods: list[str] = []
    _brand_extra_patches: dict[str, str] = {}
    mpl: Axes  # MethodProxy at runtime, typed as Axes for IDE

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        decorated, extra_patches = collect_brand_methods(cls)
        explicit = list(cls.__dict__.get("_brand_methods", []))
        merged = list(dict.fromkeys(explicit + decorated))
        if merged:
            cls._brand_methods = merged
        cls_extra = dict(cls.__dict__.get("_brand_extra_patches", {}))
        cls_extra.update(extra_patches)
        if cls_extra:
            cls._brand_extra_patches = cls_extra


def patch_axes(
    ax,
    brand_cls: type,
    *,
    methods: list[str] | None = None,
    style_fn=None,
    extra_patches: dict[str, str] | None = None,
    proxy_attr: str = "mpl",
    marker_attr: str = "_is_branded",
    twinx_fn=None,
    twiny_fn=None,
    patch_legend: bool = True,
    **style_kwargs,
) -> None:
    """Bind brand methods onto a matplotlib Axes.

    Parameters
    ----------
    ax :
        A matplotlib Axes instance.
    brand_cls :
        Subclass of :class:`BrandAxes`.
    methods :
        Method names to patch. Defaults to ``brand_cls._brand_methods``.
    style_fn :
        Optional ``(ax, **kw) -> None`` called after patching.
    extra_patches :
        ``{target_name: source_name}`` for renamed methods.
        Defaults to ``brand_cls._brand_extra_patches`` (populated
        automatically by ``@brand_method(overwrite=...)``).
    proxy_attr :
        Attribute name for :class:`MethodProxy`.
    marker_attr :
        Attribute set to prevent double-patching.
    twinx_fn, twiny_fn :
        Optional replacements for ``ax.twinx()`` / ``ax.twiny()``.
    patch_legend :
        If False, restore original ``legend`` after patching.
    **style_kwargs :
        Passed to *style_fn*.
    """
    from matplotlib.axes import Axes

    if getattr(ax, marker_attr, False):
        return

    setattr(ax, marker_attr, True)
    setattr(ax, proxy_attr, MethodProxy(ax, Axes))

    for name in methods or getattr(brand_cls, "_brand_methods", []):
        patch_method(ax, brand_cls, name)

    all_extra = dict(getattr(brand_cls, "_brand_extra_patches", {}))
    if extra_patches:
        all_extra.update(extra_patches)
    for target_name, source_name in all_extra.items():
        patch_method(ax, brand_cls, target_name, source_name)

    if not patch_legend and hasattr(ax, proxy_attr):
        ax.legend = getattr(ax, proxy_attr).legend

    if twinx_fn is not None:
        ax.twinx = functools.partial(twinx_fn, ax)
    if twiny_fn is not None:
        ax.twiny = functools.partial(twiny_fn, ax)

    if style_fn is not None:
        style_fn(ax, **style_kwargs)
