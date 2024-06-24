import math
from typing import Callable, Concatenate, ParamSpec, Any

import numpy as np
import numpy.typing as npt
from bokeh.core.enums import Place, RenderLevel
from bokeh.layouts import layout
from bokeh.models import Range1d, Toolbar, PanTool, WheelZoomTool, BoxZoomTool, ResetTool, Band, ColumnDataSource
from bokeh.palettes import Sunset8, Blues8, Blues
from bokeh.plotting import figure, show
from scipy import stats

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


def create_marginal_2d_contour_figure(marginal_2d_array0: npt.NDArray, marginal_2d_array1: npt.NDArray) -> figure:
    figure_ = figure()
    combined_marginal_2d_array = np.stack([marginal_2d_array0, marginal_2d_array1], axis=0)

    kde = stats.gaussian_kde(combined_marginal_2d_array)
    contour_x_plotting_range = get_padded_range_for_array(marginal_2d_array0)
    contour_y_plotting_range = get_padded_range_for_array(marginal_2d_array1)

    # Evaluate the KDE on a grid
    x_positions = np.linspace(*contour_x_plotting_range, 1000)
    y_positions = np.linspace(*contour_y_plotting_range, 1000)
    x_meshgrid, y_meshgrid = np.meshgrid(x_positions, y_positions)
    positions = np.vstack([x_meshgrid.ravel(), y_meshgrid.ravel()])
    z_meshgrid = kde(positions).reshape(x_meshgrid.shape)

    # Sort the KDE values
    sorted_z_meshgrid = np.sort(z_meshgrid.ravel())[::-1]

    # Compute the cumulative density
    cumulative_density = np.cumsum(sorted_z_meshgrid) / np.sum(sorted_z_meshgrid)
    threshold_indexes = np.searchsorted(cumulative_density, [0.6827, 0.9545, 0.9973])
    thresholds = sorted_z_meshgrid[threshold_indexes]
    thresholds = thresholds[::-1]
    # thresholds = np.concat([np.array([np.min(sorted_z_meshgrid)]), thresholds, np.array([np.max(sorted_z_meshgrid)])])
    thresholds = np.concat([thresholds, np.array([np.max(sorted_z_meshgrid)])])

    fill_palette = Blues[len(thresholds - 1)][::-1]
    contour_renderer = figure_.contour(x=x_meshgrid, y=y_meshgrid, z=z_meshgrid, levels=thresholds,
                                       fill_color=fill_palette, fill_alpha=0.8)
    return figure_


def create_marginal_1d_contour_figure(marginal_1d_array: npt.NDArray) -> figure:
    figure_ = figure()

    kde = stats.gaussian_kde(marginal_1d_array)
    distribution_plotting_range = get_padded_range_for_array(marginal_1d_array)

    # Evaluate the KDE on a grid
    plotting_positions = np.linspace(*distribution_plotting_range, 1000)
    distribution_values = kde(plotting_positions)
    confidence_interval_thresholds = np.array([0.6827, 0.9545, 0.9973])
    half_confidence_interval_thresholds = confidence_interval_thresholds / 2
    quantile_thresholds = np.concat([
        0.5 - half_confidence_interval_thresholds[::-1],  # The lower bounds of the intervals.
        np.array([0.5]),  # The median.
        0.5 + half_confidence_interval_thresholds,  # The upper bounds of the intervals.
    ])

    threshold_values = np.quantile(plotting_positions, quantile_thresholds, weights=distribution_values, method='inverted_cdf')
    plotting_position_threshold_indexes = np.searchsorted(plotting_positions, threshold_values)
    interval_segment_plotting_positions = np.split(plotting_positions, plotting_position_threshold_indexes)
    # TODO: Include next value of array in split to make sure there are no gaps.
    interval_segment_values = np.split(distribution_values, plotting_position_threshold_indexes)
    palette = Blues[len(confidence_interval_thresholds)]
    for confidence_interval_threshold_index in range(len(confidence_interval_thresholds)):
        lower_segment_positions = interval_segment_plotting_positions[confidence_interval_threshold_index + 1]
        upper_segment_positions = interval_segment_plotting_positions[-(confidence_interval_threshold_index + 2)]
        lower_segment_values = interval_segment_values[confidence_interval_threshold_index + 1]
        upper_segment_values = interval_segment_values[-(confidence_interval_threshold_index + 2)]
        lower_column_data_source = ColumnDataSource(data={
            'base': lower_segment_positions,
            'lower': np.zeros_like(lower_segment_values),
            'upper': lower_segment_values,
        })
        upper_column_data_source = ColumnDataSource(data={
            'base': upper_segment_positions,
            'lower': np.zeros_like(upper_segment_values),
            'upper': upper_segment_values,
        })
        lower_band = Band(source=lower_column_data_source, base='base', lower='lower', upper='upper', fill_color=palette[-(confidence_interval_threshold_index + 1)], fill_alpha=0.8)
        upper_band = Band(source=upper_column_data_source, base='base', lower='lower', upper='upper', fill_color=palette[-(confidence_interval_threshold_index + 1)], fill_alpha=0.8)
        figure_.add_layout(lower_band)
        figure_.add_layout(upper_band)
    median_position_index = plotting_position_threshold_indexes[math.floor(plotting_position_threshold_indexes.shape[0]/2)]
    median_value = distribution_values[median_position_index]
    median_position = plotting_positions[median_position_index]
    figure_.line(x=[median_position, median_position], y=[0, median_value])
    figure_.line(x=plotting_positions, y=distribution_values)
    return figure_


def get_range_1d_for_array(array: npt.NDArray, padding_fraction: float = 0.05) -> Range1d:
    range_end, range_start = get_padded_range_for_array(array, padding_fraction)
    range_1d = Range1d(start=range_start, end=range_end)
    return range_1d


def get_padded_range_for_array(array, padding_fraction: float = 0.05) -> (float, float):
    array_minimum = np.min(array)
    array_maximum = np.max(array)
    array_difference = array_maximum - array_minimum
    padding = padding_fraction * array_difference
    range_start = array_minimum - padding
    range_end = array_maximum + padding
    return range_start, range_end


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
    x_ranges = [get_range_1d_for_array(array[:, index])
                for index in range(number_of_parameters)]
    y_ranges = [get_range_1d_for_array(array[:, index])
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
    data_ = np.random.multivariate_normal([0, 0],
                                          [[0.0, 1.0], [1.0, 0.0]],
                                          100)
    data_ = np.stack([np.random.normal(size=1000), np.random.normal(size=1000)], axis=1)
    create_corner_plot(data_, marginal_2d_figure_function=create_marginal_2d_contour_figure,
                       marginal_1d_figure_function=create_marginal_1d_contour_figure)
