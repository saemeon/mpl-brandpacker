"""Tests for mpl_brandpacker.colors."""

import pytest

from mpl_brandpacker.colors import ColorsBase


class TestColorsBase:
    def test_valid_hex(self):
        class C(ColorsBase):
            red = "#ff0000"
            blue = "#0000ff"

        assert C.red == "#ff0000"
        assert C.blue == "#0000ff"

    def test_named_color(self):
        class C(ColorsBase):
            r = "red"
            b = "blue"

        assert C.r == "#ff0000"
        assert C.b == "#0000ff"

    def test_short_hex(self):
        class C(ColorsBase):
            white = "#fff"

        assert C.white == "#ffffff"

    def test_hex_with_alpha(self):
        class C(ColorsBase):
            semi = "#ff000080"

        assert C.semi == "#ff000080"

    def test_opaque_alpha_stripped(self):
        class C(ColorsBase):
            full = "#ff0000ff"

        assert C.full == "#ff0000"

    def test_short_hex_with_alpha(self):
        class C(ColorsBase):
            semi = "#f008"

        assert C.semi == "#ff000088"

    def test_cn_color(self):
        class C(ColorsBase):
            first = "C0"

        # C0 resolves to the first color in the default cycle
        assert C.first.startswith("#")

    def test_rejects_invalid(self):
        with pytest.raises(ValueError, match="not a valid color"):

            class C(ColorsBase):
                bad = "not_a_color_at_all"

    def test_is_str(self):
        class C(ColorsBase):
            x = "#aabbcc"

        assert isinstance(C.x, str)
        assert C.x == "#aabbcc"

    def test_printable_repr(self):
        class C(ColorsBase):
            """My colors."""

            a = "#111111"
            b = "#222222"

        r = repr(C)
        assert "a" in r
        assert "b" in r

    def test_dict_access(self):
        class C(ColorsBase):
            primary = "#123456"

        assert C["primary"] == "#123456"

    def test_dash_to_underscore(self):
        class C(ColorsBase):
            light_blue = "#aabbcc"

        assert C["light-blue"] == "#aabbcc"

    def test_css_named_colors(self):
        class C(ColorsBase):
            coral = "coral"
            teal = "teal"
            gold = "gold"

        assert C.coral.startswith("#")
        assert C.teal.startswith("#")
        assert C.gold.startswith("#")

    def test_tab_colors(self):
        class C(ColorsBase):
            blue = "tab:blue"
            orange = "tab:orange"

        assert C.blue.startswith("#")
        assert C.orange.startswith("#")
