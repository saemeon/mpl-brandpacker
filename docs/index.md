# mpl-brandpacker

Package your brand design into a `matplotlib.pyplot` drop-in replacement. Define titles, headers styling, colors, and axes styling as Python classes — mpl-brandpacker handles the patching so `your_brand.pyplot.subplots()` returns fully branded figures and axes.

## Install

```bash
pip install mpl-brandpacker
```

## Quick start

### 1. Define your brand

```python
# my_brand/colors.py
import mpl_brandpacker as mbp

class Colors(mbp.ColorsBase):
    primary = "#1a5276"
    accent = "#e67e22"
    dark = "#2c3e50"
    muted = "slategray"       # named colors work too

Colors.plot()  # → swatch grid for documentation
```

`ColorsBase` accepts any matplotlib color string (`#RRGGBB`, `#RRGGBBAA`, `#RGB`, named colors, `C0`–`C9`, `tab:blue`, etc.) and normalizes to `#rrggbb` at definition time.

```python
# my_brand/sizes.py
from mpl_brandpacker.sizes import MM_TO_INCH

class Sizes(mbp.FigsizesBase):
    half = (88 * MM_TO_INCH, 76 * MM_TO_INCH)
    full = (181 * MM_TO_INCH, 76 * MM_TO_INCH)

class FontSizes(mbp.SizesBase):
    title = 10
    body = 8
    footer = 6.5

    _scalers = {"presentation": 2.0}
```

`SizesBase.scaled()` is thread-safe — concurrent threads and async tasks each get their own scaled values.

```python
# my_brand/figure.py
from mpl_brandpacker import BrandFigure, brand_method

class MyFigure(BrandFigure):
    @brand_method
    def set_title(self, title, **kw):
        self.mpl.suptitle(title, fontsize=10, weight="bold", x=0.02, ha="left", **kw)

    @brand_method
    def set_sources(self, sources, **kw):
        self.text(0.02, 0.02, f"Source: {sources}", fontsize=6.5,
                  color="#888", transform=self.transFigure, **kw)

    @brand_method(overwrite="savefig")
    def _branded_save(self, *args, **kw):
        """Override savefig — Pylance still shows the original docstring."""
        kw.setdefault("dpi", 300)
        kw.setdefault("bbox_inches", "tight")
        self.mpl.savefig(*args, **kw)
```

Use `@brand_method(overwrite="name")` to override a built-in method while keeping IDE autocompletion on the original.

```python
# my_brand/axes.py
from mpl_brandpacker import BrandAxes, brand_method

class MyAxes(BrandAxes):
    @brand_method
    def set_xlabel(self, label, **kw):
        self.mpl.set_xlabel(label, fontsize=8, **kw)

    @brand_method
    def set_ylabel(self, label, **kw):
        self.mpl.set_ylabel(label, fontsize=8, rotation="horizontal", **kw)

def set_style(ax, **kw):
    ax.grid(True, alpha=0.2)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
```

### 2. Configure

```python
# my_brand/__init__.py
import mpl_brandpacker as mbp
from pathlib import Path

mbp.configure(
    figure_cls=MyFigure,
    axes_cls=MyAxes,
    style_fn=set_style,
    stylesheet=Path(__file__).parent,  # dir with .mplstyle + data/fonts/
    pandas=True,                        # also hook df.plot()
)
```

### 3. Re-export pyplot

```python
# my_brand/pyplot.py
from mpl_brandpacker.pyplot import *  # noqa
from mpl_brandpacker.pyplot import gcf

# pyplot-level shortcuts for brand methods (like plt.title in matplotlib)
def title(title, **kw):     gcf().set_title(title, **kw)
def subtitle(sub, **kw):    gcf().set_subtitle(sub, **kw)
def sources(src, **kw):     gcf().set_sources(src, **kw)
def footnote(note, **kw):   gcf().set_footnote(note, **kw)
```

For IDE autocompletion of brand methods on `fig` and `ax`, add a `pyplot.pyi` stub file — see the [template](https://github.com/saemeon/mpl-brandpacker/tree/main/template) for a complete example.

### 4. Use it

```python
import my_brand.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
ax.set_xlabel("Quarter")

plt.title("Revenue")
plt.sources("Bloomberg")
plt.show()
```

Everything is branded. Original matplotlib methods are accessible via `.mpl`:

```python
fig.mpl.legend()       # original Figure.legend
ax.mpl.set_xlabel()    # original Axes.set_xlabel
```

### 5. Reset (notebooks)

When iterating on your brand in a notebook, use `reset()` to start fresh:

```python
import mpl_brandpacker as mbp

mbp.reset()                          # clears all hooks, reverts pandas
mbp.configure(figure_cls=..., ...)   # re-configure
```

## API Reference

### configure

::: mpl_brandpacker.configure

### reset

::: mpl_brandpacker.reset

### brand_method

::: mpl_brandpacker.patcher.brand_method

### BrandFigure

::: mpl_brandpacker.figure.BrandFigure

### BrandAxes

::: mpl_brandpacker.axes.BrandAxes

### ColorsBase

::: mpl_brandpacker.colors.ColorsBase

### FigsizesBase

::: mpl_brandpacker.sizes.FigsizesBase

### SizesBase

::: mpl_brandpacker.sizes.SizesBase
