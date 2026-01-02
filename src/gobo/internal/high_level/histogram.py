from bokeh.plotting import figure
from numpy import typing as npt

from gobo.internal.histogram import add_1d_histogram_to_figure


def create_histogram_figure(
        data: npt.NDArray,
        *args,
        bins: int = 30,
        **kwargs,
) -> figure:
    figure_ = figure(*args, **kwargs)
    add_1d_histogram_to_figure(figure_, data, bins=bins)
    return figure_
