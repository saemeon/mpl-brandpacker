"""Base class for brand color enums.

Accepts any color format that matplotlib understands and normalizes to hex
at class definition time.

Example::

    from mpl_brandpacker.colors import ColorsBase

    class Colors(ColorsBase):
        primary = "#2563eb"
        secondary = "slategray"
        semi = "#2563eb80"                  # hex with alpha
        short = "#fab"                      # short hex
        cycle = "C0"                        # matplotlib cycle colors
        css = "coral"                       # CSS named colors

    Colors.plot()  # → swatch grid
"""

from __future__ import annotations

from matplotlib.colors import to_hex

from mpl_brandpacker.utils import PrintableEnum


class ColorsBase(str, PrintableEnum):
    """Base class for brand color palettes.

    Accepts any string color that matplotlib understands:

    - Hex strings: ``"#RGB"``, ``"#RRGGBB"``, ``"#RGBA"``, ``"#RRGGBBAA"``
    - Named colors: ``"red"``, ``"slategray"``, ``"coral"``
    - Cycle colors: ``"C0"``, ``"C1"``, ``"tab:blue"``

    All values are normalized to ``"#rrggbb"`` (or ``"#rrggbbaa"`` when
    alpha < 1) at definition time so they can be used directly as strings.

    Call ``MyColors.plot()`` to display a swatch grid of all colors.
    """

    def __new__(cls, value):
        try:
            # Keep alpha when present (keep_alpha=True), normalize to hex
            hexval = to_hex(value, keep_alpha=True)
            # Strip alpha suffix if fully opaque (#rrggbbff → #rrggbb)
            if len(hexval) == 9 and hexval.endswith("ff"):
                hexval = hexval[:7]
        except ValueError:
            raise ValueError(
                f"{cls.__name__}: {value!r} is not a valid color. "
                f"Use any matplotlib color format: '#RRGGBB', '#RRGGBBAA', "
                f"named colors ('red', 'C0'), or RGB/RGBA tuples."
            ) from None
        return str.__new__(cls, hexval)

    @classmethod
    def plot(cls, figsize=None, columns=4):
        """Display a swatch grid of all colors.

        Parameters
        ----------
        figsize :
            Figure size. Auto-computed if None.
        columns :
            Number of columns in the grid.
        """
        import matplotlib.patches as patches
        import matplotlib.pyplot as plt

        names = list(cls.__members__.keys())
        n = len(names)
        rows = (n + columns - 1) // columns

        if figsize is None:
            figsize = (columns * 2.2, rows * 0.6)

        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(0, columns)
        ax.set_ylim(0, rows)
        ax.axis("off")
        ax.set_title(cls.__name__, fontsize=12, weight="bold", loc="left")

        for i, name in enumerate(names):
            col = i % columns
            row = rows - 1 - i // columns
            color = cls[name].value

            rect = patches.FancyBboxPatch(
                (col + 0.05, row + 0.1),
                0.4,
                0.4,
                boxstyle="round,pad=0.02",
                facecolor=color,
                edgecolor="#ddd",
                linewidth=0.5,
            )
            ax.add_patch(rect)
            ax.text(col + 0.55, row + 0.35, name, fontsize=8, va="center")
            ax.text(
                col + 0.55, row + 0.15, color, fontsize=6.5, va="center", color="#888"
            )

        fig.tight_layout()
        return fig
