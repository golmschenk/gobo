from __future__ import annotations

import numpy as np
from bokeh.plotting import figure
from numpy import typing as npt


def create_histogram_figure(array: npt.NDArray) -> figure:
    figure_ = figure()
    add_1d_histogram_to_figure(figure_, array)
    return figure_


def add_1d_histogram_to_figure(figure_, array):
    hist, edges = np.histogram(array, density=True, bins=30)
    figure_.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
