"""Tests for mpl_brandpacker.configure."""

import warnings

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

import mpl_brandpacker
from mpl_brandpacker._config import is_configured
from mpl_brandpacker.axes import BrandAxes
from mpl_brandpacker.figure import BrandFigure
from mpl_brandpacker.patcher import brand_method


class _MyFig(BrandFigure):
    _brand_methods = ["set_title"]

    def set_title(self, title):
        self._test_title = title


class _MyAx(BrandAxes):
    _brand_methods = ["set_xlabel"]

    def set_xlabel(self, label):
        self._test_label = label


class TestConfigure:
    def test_basic(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        assert is_configured()

    def test_with_style_fn(self):
        styled = []
        mpl_brandpacker.configure(
            figure_cls=_MyFig,
            axes_cls=_MyAx,
            style_fn=lambda ax, **kw: styled.append(True),
        )
        assert is_configured()

    def test_double_configure_warns(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
            assert len(w) == 1
            assert "overwriting" in str(w[0].message)

    def test_validates_brand_methods(self):
        class BadFig(BrandFigure):
            _brand_methods = ["nonexistent"]

        with pytest.raises(ValueError, match="nonexistent.*not defined"):
            mpl_brandpacker.configure(figure_cls=BadFig)

    def test_validates_axes_brand_methods(self):
        class BadAx(BrandAxes):
            _brand_methods = ["nonexistent"]

        with pytest.raises(ValueError, match="nonexistent.*not defined"):
            mpl_brandpacker.configure(axes_cls=BadAx)

    def test_auto_wires_make_ax_on_figure(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)

        fig = plt.figure()
        from mpl_brandpacker._config import get_make_fig

        get_make_fig()(fig)

        ax = fig.add_subplot(111)
        assert hasattr(ax, "_is_branded")
        plt.close(fig)


class TestPyplotIntegration:
    def test_subplots_patches_both(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        import mpl_brandpacker.pyplot as bplt

        fig, ax = bplt.subplots()
        fig.set_title("test")
        ax.set_xlabel("x")
        assert fig._test_title == "test"
        assert ax._test_label == "x"
        bplt.close("all")

    def test_2x2_subplots(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        import mpl_brandpacker.pyplot as bplt

        fig, axes = bplt.subplots(2, 2)
        assert all(hasattr(a, "_is_branded") for row in axes for a in row)
        bplt.close("all")

    def test_gcf_patches(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        import mpl_brandpacker.pyplot as bplt

        bplt.figure()
        fig = bplt.gcf()
        assert hasattr(fig, "_is_branded")
        bplt.close("all")


class TestReset:
    def test_reset_clears_config(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        assert is_configured()
        mpl_brandpacker.reset()
        assert not is_configured()

    def test_configure_after_reset_no_warning(self):
        mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
        mpl_brandpacker.reset()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            mpl_brandpacker.configure(figure_cls=_MyFig, axes_cls=_MyAx)
            assert len(w) == 0

    def test_reset_when_not_configured(self):
        mpl_brandpacker.reset()  # should not raise
        assert not is_configured()


class TestBrandMethodDecorator:
    def test_decorator_auto_discovery(self):
        class MyFig(BrandFigure):
            @brand_method
            def set_title(self, title):
                self._test_title = title

            @brand_method
            def set_sources(self, src):
                self._test_sources = src

        assert "set_title" in MyFig._brand_methods
        assert "set_sources" in MyFig._brand_methods

    def test_decorator_works_with_configure(self):
        class MyFig(BrandFigure):
            @brand_method
            def set_title(self, title):
                self._test_title = title

        class MyAx(BrandAxes):
            @brand_method
            def set_xlabel(self, label):
                self._test_label = label

        mpl_brandpacker.configure(figure_cls=MyFig, axes_cls=MyAx)
        assert is_configured()

    def test_mixed_decorator_and_list(self):
        class MyFig(BrandFigure):
            _brand_methods = ["set_title"]

            def set_title(self, title):
                self._test_title = title

            @brand_method
            def set_sources(self, src):
                self._test_sources = src

        assert "set_title" in MyFig._brand_methods
        assert "set_sources" in MyFig._brand_methods

    def test_no_duplicates(self):
        class MyFig(BrandFigure):
            _brand_methods = ["set_title"]

            @brand_method
            def set_title(self, title):
                self._test_title = title

        assert MyFig._brand_methods.count("set_title") == 1

    def test_decorator_on_axes(self):
        class MyAx(BrandAxes):
            @brand_method
            def zeroline(self):
                pass

            @brand_method
            def set_xlabel(self, label):
                pass

        assert "zeroline" in MyAx._brand_methods
        assert "set_xlabel" in MyAx._brand_methods

    def test_overwrite_on_figure(self):
        class MyFig(BrandFigure):
            @brand_method
            def set_title(self, title):
                self._test_title = title

            @brand_method(overwrite="savefig")
            def _branded_save(self, *args, **kw):
                self._save_called = True

        # _branded_save should NOT be in _brand_methods (it has overwrite)
        assert "_branded_save" not in MyFig._brand_methods
        # but should be in _brand_extra_patches
        assert MyFig._brand_extra_patches == {"savefig": "_branded_save"}

    def test_overwrite_patches_at_runtime(self):
        class MyFig(BrandFigure):
            @brand_method(overwrite="savefig")
            def _branded_save(self, *args, **kw):
                self._save_called = True

        mpl_brandpacker.configure(figure_cls=MyFig)
        import mpl_brandpacker.pyplot as bplt

        fig = bplt.figure()
        fig.savefig("/dev/null")
        assert fig._save_called is True
        bplt.close("all")

    def test_overwrite_on_axes(self):
        class MyAx(BrandAxes):
            @brand_method(overwrite="set_xlabel")
            def _branded_xlabel(self, label, **kw):
                self._custom_label = label

        assert MyAx._brand_extra_patches == {"set_xlabel": "_branded_xlabel"}
        assert "_branded_xlabel" not in MyAx._brand_methods

    def test_overwrite_preserves_original_via_mpl(self):
        import io

        saved_args = []

        class MyFig(BrandFigure):
            @brand_method(overwrite="savefig")
            def _branded_save(self, *args, **kw):
                saved_args.append(("branded", args, kw))

        mpl_brandpacker.configure(figure_cls=MyFig)
        import mpl_brandpacker.pyplot as bplt

        fig = bplt.figure()
        # Branded version — doesn't actually save, just records
        fig.savefig(io.BytesIO())
        assert len(saved_args) == 1
        # Original via .mpl — bypasses branded version
        fig.mpl.savefig(io.BytesIO(), format="png")
        assert len(saved_args) == 1  # mpl.savefig doesn't go through branded
        bplt.close("all")
