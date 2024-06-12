from typing import Callable

import numpy as np
import numpy.typing as npt
from bokeh.core.enums import Place
from bokeh.layouts import layout
from bokeh.models import Range1d, Toolbar, PanTool, WheelZoomTool, BoxZoomTool, ResetTool
from bokeh.plotting import figure, show


def create_marginal_1d_histogram_figure(marginal_1d_array: npt.NDArray) -> figure:
    figure_ = figure()
    hist, edges = np.histogram(marginal_1d_array, density=True, bins=30)
    figure_.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
    return figure_


def create_marginal_2d_scatter_figure(marginal_2d_array0: npt.NDArray, marginal_2d_array1: npt.NDArray) -> figure:
    figure_ = figure()
    figure_.scatter(marginal_2d_array0, marginal_2d_array1, size=3, alpha=0.5)
    return figure_


def create_corner_plot(
        array: npt.NDArray,
        *,
        marginal_1d_figure_function: Callable[[npt.NDArray], figure] = create_marginal_1d_histogram_figure,
        marginal_2d_figure_function: Callable[[npt.NDArray, npt.NDArray], figure] = create_marginal_2d_scatter_figure,
):
    assert len(array.shape) == 2

    # Prepare shared components.
    x_ranges = [Range1d(start=np.min(array[:, index]), end=np.max(array[:, index])) for index in range(array.shape[1])]
    y_ranges = [Range1d(start=np.min(array[:, index]), end=np.max(array[:, index])) for index in range(array.shape[1])]
    tools = [PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool()]
    toolbar = Toolbar(tools=tools)

    plots = []

    for row_index in range(array.shape[1]):
        row_figures: list[figure] = []
        for column_index in range(array.shape[1]):
            figure_ = None
            subfigure_size = 200
            end_axis_minimum_border = 100
            subfigure_min_border = 5
            # 1D marginal distribution figures.
            if row_index == column_index:
                marginal_1d_array = array[:, row_index]
                figure_ = marginal_1d_figure_function(marginal_1d_array)
                if len(figure_.left) > 0:
                    axis = figure_.left.pop(0)
                    figure_.add_layout(axis, Place.right)
                figure_.xaxis.visible = False
                figure_.yaxis.visible = True
                figure_.min_border = subfigure_min_border
                if column_index == 0:
                    figure_.min_border_left = end_axis_minimum_border
            # 2D marginal distribution figures.
            elif row_index > column_index:
                marginal_2d_array0 = array[:, column_index]
                marginal_2d_array1 = array[:, row_index]
                figure_ = marginal_2d_figure_function(marginal_2d_array0, marginal_2d_array1)
                figure_.min_border = subfigure_min_border
                if column_index == 0:
                    figure_.min_border_left = end_axis_minimum_border
                else:
                    figure_.yaxis.visible = False
                if row_index == array.shape[1] - 1:
                    figure_.min_border_bottom = end_axis_minimum_border
                else:
                    figure_.xaxis.visible = False
                figure_.y_range = y_ranges[row_index]
            if figure_ is not None:
                if row_index == array.shape[1] - 1 and column_index == array.shape[1] - 1:
                    figure_.toolbar_location = Place.below
                else:
                    figure_.toolbar_location = None
                figure_.frame_width = subfigure_size
                figure_.frame_height = subfigure_size
                figure_.x_range = x_ranges[column_index]
                figure_.toolbar = toolbar
                row_figures.append(figure_)
        plots.append(row_figures)

    # Create a grid plot
    layout_ = layout(*plots)

    # Display the plot
    show(layout_)


if __name__ == '__main__':
    data_ = np.random.multivariate_normal([0, 0, 0, 1000],
                                          [[1, 0.2, 1, 0.1], [0.2, 1, 1, 0.1], [1, 1, 1, 1], [1, 1, 1, 1]],
                                          1000)
    create_corner_plot(data_)
