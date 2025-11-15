from __future__ import annotations

from typing import Callable, Any

import numpy as np
from bokeh.plotting import figure
from numpy import typing as npt


def create_histogram_figure(array: npt.NDArray, *, bins: int = 30, figure_function: Callable[[..., Any], figure] | None = None) -> figure:
    if figure_function is None:
        figure_function = figure
    figure_ = figure_function()
    add_1d_histogram_to_figure(figure_, array, bins=bins)
    return figure_


def add_1d_histogram_to_figure(figure_, array, *, bins):
    hist, edges = np.histogram(array, density=True, bins=bins)
    figure_.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
