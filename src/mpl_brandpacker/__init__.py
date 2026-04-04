"""mpl-brandpacker — build branded matplotlib packages.

A framework for creating company-specific matplotlib packages. Define
your corporate design (colors, fonts, header/footer, axes styling) as
Python classes, call ``configure()``, and get a branded ``pyplot`` that
works as a drop-in for ``matplotlib.pyplot``.

Quick start
-----------

1. **Subclass** the base classes to define your brand::

    import mpl_brandpacker as mbp

    class MyColors(mbp.ColorsBase):
        primary = "#2563eb"
        accent = "#f59e0b"

    class MySizes(mbp.FigsizesBase):
        half = (3.46, 2.99)
        full = (6.93, 5.14)

    class MyFigure(mbp.BrandFigure):
        @mbp.brand_method
        def set_title(self, title): ...

        @mbp.brand_method
        def set_sources(self, sources): ...

        @mbp.brand_method(overwrite="savefig")
        def _branded_save(self, *a, **kw):
            '''Override savefig while keeping Pylance's original docstring.'''
            self.mpl.savefig(*a, dpi=300, **kw)

    class MyAxes(mbp.BrandAxes):
        @mbp.brand_method
        def set_xlabel(self, label): ...

2. **Configure** once at import time::

    mbp.configure(
        figure_cls=MyFigure,
        axes_cls=MyAxes,
        style_fn=set_my_style,          # optional: (ax, **kw) -> None
        stylesheet=Path(__file__).parent, # optional: dir with .mplstyle + data/fonts/
        pandas=True,                      # optional: also hook df.plot()
    )

3. **Re-export** pyplot and add brand shortcuts::

    # my_brand/pyplot.py
    from mpl_brandpacker.pyplot import *  # noqa
    from mpl_brandpacker.pyplot import gcf

    def title(t, **kw):    gcf().set_title(t, **kw)
    def sources(s, **kw):  gcf().set_sources(s, **kw)

4. **Users** just import your package::

    import my_brand.pyplot as plt
    fig, ax = plt.subplots()   # automatically branded
    fig.set_title("Q4 Revenue")
    plt.sources("Bloomberg")   # pyplot-level brand shortcut
    fig.mpl.legend()           # access original matplotlib methods via .mpl

5. **Reset** (e.g. in notebooks when iterating)::

    mbp.reset()                          # clears all hooks, reverts pandas
    mbp.configure(figure_cls=..., ...)   # re-configure with new settings

Submodules (advanced)
---------------------

- ``mpl_brandpacker.pyplot`` — branded drop-in for matplotlib.pyplot
- ``mpl_brandpacker.pandas`` — ``use_for_pandas()`` for manual df.plot() opt-in
- ``mpl_brandpacker.patcher`` — low-level ``patch_method()``, ``MethodProxy``,
  ``brand_method``
- ``mpl_brandpacker.style`` — ``register_stylesheet()``
- ``mpl_brandpacker.sizes`` — ``MM_TO_INCH``, ``POINTS_TO_INCH``
- ``mpl_brandpacker.utils`` — ``get_text_bbox()``, ``separate_kwargs()``
"""

from mpl_brandpacker._config import configure, reset
from mpl_brandpacker.axes import BrandAxes
from mpl_brandpacker.colors import ColorsBase
from mpl_brandpacker.figure import BrandFigure
from mpl_brandpacker.patcher import brand_method
from mpl_brandpacker.sizes import FigsizesBase, SizesBase
from mpl_brandpacker.utils import PrintableEnum

__all__ = [
    "configure",
    "reset",
    "brand_method",
    "BrandFigure",
    "BrandAxes",
    "ColorsBase",
    "FigsizesBase",
    "SizesBase",
    "PrintableEnum",
]
