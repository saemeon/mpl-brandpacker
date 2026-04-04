"""Low-level patching utilities for binding methods onto matplotlib objects.

This module provides the building blocks used by :mod:`mpl_brandpacker.figure`
and :mod:`mpl_brandpacker.axes`.  Most users should use those higher-level
modules directly.

- ``brand_method`` — decorator that marks a method for auto-patching
- ``patch_method()`` — bind a single method from one class onto an instance
- ``MethodProxy`` — access original (unpatched) methods via ``obj.mpl``
"""

from __future__ import annotations

import functools
from typing import Any

_BRAND_METHOD_ATTR = "_is_brand_method"
_BRAND_OVERWRITE_ATTR = "_brand_overwrite"


def brand_method(fn=None, *, overwrite: str | None = None):
    """Mark a method for automatic brand patching.

    Decorated methods are auto-discovered by
    :class:`BrandFigure` and :class:`BrandAxes`.

    Parameters
    ----------
    overwrite :
        Target method name on the matplotlib object. When omitted, the
        method replaces the one with the same name. Use this to override
        a built-in method while keeping your implementation
        underscore-prefixed (invisible to Pylance on the brand class,
        so IDE users still see the original docstring).

    Examples::

        class MyFigure(BrandFigure):
            @brand_method
            def set_title(self, title, **kw):
                self.mpl.suptitle(title, fontsize=10)

            @brand_method(overwrite="savefig")
            def _branded_savefig(self, *args, **kw):
                # custom save logic — Pylance still shows Figure.savefig docs
                self.mpl.savefig(*args, dpi=300, **kw)
    """

    def _decorator(fn):
        setattr(fn, _BRAND_METHOD_ATTR, True)
        if overwrite is not None:
            setattr(fn, _BRAND_OVERWRITE_ATTR, overwrite)
        return fn

    # Support both @brand_method and @brand_method(overwrite="savefig")
    if fn is not None:
        return _decorator(fn)
    return _decorator


def collect_brand_methods(cls: type) -> tuple[list[str], dict[str, str]]:
    """Collect methods marked with :func:`brand_method` on *cls*.

    Returns
    -------
    methods :
        Names of methods that patch the same-named target (no ``overwrite``).
    extra_patches :
        ``{target_name: source_name}`` for methods with ``overwrite``.
    """
    methods: list[str] = []
    extra_patches: dict[str, str] = {}
    seen: set[str] = set()
    for klass in cls.__mro__:
        for name, obj in vars(klass).items():
            if name in seen or not getattr(obj, _BRAND_METHOD_ATTR, False):
                continue
            seen.add(name)
            target = getattr(obj, _BRAND_OVERWRITE_ATTR, None)
            if target is not None:
                extra_patches[target] = name
            else:
                methods.append(name)
    return methods, extra_patches


def patch_method(target, source, name: str, source_name: str | None = None) -> None:
    """Bind a method from *source* class onto *target* instance.

    Uses the descriptor protocol (``__get__``) to bind the method as if
    it were defined on ``type(target)``.

    Parameters
    ----------
    target :
        Instance to patch (e.g. a Figure or Axes).
    source :
        Class to retrieve the method from (e.g. BrandFigure).
    name :
        Attribute name to set on *target*.
    source_name :
        Method name to retrieve from *source*. Defaults to *name*.
    """
    if source_name is None:
        source_name = name
    setattr(target, name, getattr(source, source_name).__get__(target, type(target)))


class MethodProxy:
    """Proxy that forwards calls to the original class, bypassing patches.

    After patching, ``obj.mpl.<method>()`` calls the original matplotlib
    method instead of the brand override.

    Parameters
    ----------
    instance :
        The patched object.
    cls :
        The original class (e.g. ``matplotlib.figure.Figure``).

    Example::

        fig.mpl.legend()      # original Figure.legend
        ax.mpl.set_xlabel()   # original Axes.set_xlabel
    """

    def __init__(self, instance: object, cls: type) -> None:
        self._instance = instance
        self._cls = cls

    def __getattr__(self, name: str) -> functools.partial[Any]:
        return functools.partial(getattr(self._cls, name), self._instance)
