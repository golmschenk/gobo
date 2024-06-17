from typing import Callable, Concatenate, ParamSpec, Any

import numpy as np
import numpy.typing as npt
from bokeh.core.enums import Place
from bokeh.layouts import layout
from bokeh.models import Range1d, Toolbar, PanTool, WheelZoomTool, BoxZoomTool, ResetTool
from bokeh.plotting import figure, show

P = ParamSpec('P')


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
        marginal_1d_figure_function: Callable[
            Concatenate[npt.NDArray, P], figure] = create_marginal_1d_histogram_figure,
        marginal_2d_figure_function: Callable[
            Concatenate[npt.NDArray, npt.NDArray, P], figure] = create_marginal_2d_scatter_figure,
        subfigure_size: int = 200,
        subfigure_min_border: int = 5,
        end_axis_minimum_border: int = 100,
        sub_figure_kwargs: dict[Any, Any] = None
):
    if sub_figure_kwargs is None:
        sub_figure_kwargs = {}
    assert len(array.shape) == 2

    # Prepare shared components.
    number_of_parameters = array.shape[1]
    x_ranges = [Range1d(start=np.min(array[:, index]), end=np.max(array[:, index]))
                for index in range(number_of_parameters)]
    y_ranges = [Range1d(start=np.min(array[:, index]), end=np.max(array[:, index]))
                for index in range(number_of_parameters)]
    tools = [PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool()]
    toolbar = Toolbar(tools=tools)

    plots = []

    for row_index in range(number_of_parameters):
        row_figures: list[figure] = []
        for column_index in range(number_of_parameters):
            figure_ = None
            if row_index == column_index:  # 1D marginal distribution figures.
                marginal_1d_array = array[:, row_index]
                figure_ = marginal_1d_figure_function(marginal_1d_array, **sub_figure_kwargs)
            if row_index > column_index:  # 2D marginal distribution figures.
                marginal_2d_array0 = array[:, column_index]
                marginal_2d_array1 = array[:, row_index]
                figure_ = marginal_2d_figure_function(marginal_2d_array0, marginal_2d_array1, **sub_figure_kwargs)
            if figure_ is not None:
                compose_figure_for_corner_plot_position(figure_, column_index, row_index, number_of_parameters,
                                                        x_ranges, y_ranges, toolbar, subfigure_size,
                                                        subfigure_min_border, end_axis_minimum_border)
                row_figures.append(figure_)
        plots.append(row_figures)

    # Create a grid plot
    layout_ = layout(*plots)

    # Display the plot
    show(layout_)


def compose_figure_for_corner_plot_position(figure_: figure, column_index: int, row_index: int,
                                            number_of_parameters: int, x_ranges: list[Range1d], y_ranges: list[Range1d],
                                            toolbar: Toolbar, subfigure_size: int, subfigure_min_border: int,
                                            end_axis_minimum_border: int):
    if row_index == column_index:  # 1D marginal distribution figures.
        if len(figure_.left) > 0:
            axis = figure_.left.pop(0)
            figure_.add_layout(axis, Place.right)
        figure_.xaxis.visible = False
        figure_.yaxis.visible = True
        figure_.min_border = subfigure_min_border
        if column_index == 0:
            figure_.min_border_left = end_axis_minimum_border
    if row_index > column_index:  # 2D marginal distribution figures.
        figure_.min_border = subfigure_min_border
        if column_index == 0:
            figure_.min_border_left = end_axis_minimum_border
        else:
            figure_.yaxis.visible = False
        if row_index == number_of_parameters - 1:
            figure_.min_border_bottom = end_axis_minimum_border
        else:
            figure_.xaxis.visible = False
        figure_.y_range = y_ranges[row_index]
    if row_index == number_of_parameters - 1 and column_index == number_of_parameters - 1:
        figure_.toolbar_location = Place.below
    else:
        figure_.toolbar_location = None
    figure_.frame_width = subfigure_size
    figure_.frame_height = subfigure_size
    figure_.x_range = x_ranges[column_index]
    figure_.toolbar = toolbar


if __name__ == '__main__':
    data_ = np.random.multivariate_normal([0, 0, 0, 1000],
                                          [[1, 0.2, 1, 0.1], [0.2, 1, 1, 0.1], [1, 1, 1, 1], [1, 1, 1, 1]],
                                          1000)
    create_corner_plot(data_)
