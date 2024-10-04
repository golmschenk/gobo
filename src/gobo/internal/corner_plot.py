import logging
import math
from typing import Callable, Concatenate, ParamSpec, Any

import numpy as np
import numpy.typing as npt
from bokeh.colors import Color
from bokeh.colors.named import mediumblue, firebrick
from bokeh.core.enums import Place
from bokeh.layouts import layout
from bokeh.models import Range1d, Toolbar, PanTool, WheelZoomTool, BoxZoomTool, ResetTool, Band, ColumnDataSource, \
    Column
from bokeh.palettes import varying_alpha_palette
from bokeh.plotting import figure, show
from scipy import stats

P = ParamSpec('P')

logger = logging.getLogger(__name__)


def create_histogram_figure(array: npt.NDArray) -> figure:
    figure_ = figure()
    add_1d_histogram_to_figure(figure_, array)
    return figure_


def add_1d_histogram_to_figure(figure_, array):
    hist, edges = np.histogram(array, density=True, bins=30)
    figure_.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")


def create_scatter_figure(array0: npt.NDArray, array1: npt.NDArray) -> figure:
    figure_ = figure()
    add_2d_scatter_to_figure(figure_, array0, array1, )
    return figure_


def add_2d_scatter_to_figure(figure_,
                             array0,
                             array1,
                             *,
                             color: Color = mediumblue, ):
    figure_.scatter(array0, array1, size=3, alpha=0.5, color=color)


def create_2d_kde_credible_interval_figure(array0: npt.NDArray, array1: npt.NDArray) -> figure:
    figure_ = figure()
    add_2d_kde_credible_interval_to_figure(figure_, array0, array1)
    return figure_


def add_2d_kde_credible_interval_to_figure(
        figure_: figure,
        array0: npt.NDArray,
        array1: npt.NDArray,
        *,
        color: Color = mediumblue,
):
    combined_marginal_2d_array = np.stack([array0, array1], axis=0)
    kde = stats.gaussian_kde(combined_marginal_2d_array)
    contour_x_plotting_range = get_padded_range_for_array(array0)
    contour_y_plotting_range = get_padded_range_for_array(array1)
    x_positions = np.linspace(*contour_x_plotting_range, 1000)
    y_positions = np.linspace(*contour_y_plotting_range, 1000)
    x_meshgrid, y_meshgrid = np.meshgrid(x_positions, y_positions)
    positions = np.vstack([x_meshgrid.ravel(), y_meshgrid.ravel()])
    z_meshgrid = kde(positions).reshape(x_meshgrid.shape)
    add_contour_to_figure(figure_, x_meshgrid, y_meshgrid, z_meshgrid, color)


def add_contour_to_figure(figure_, x_meshgrid, y_meshgrid, z_meshgrid, color):
    z = z_meshgrid.ravel()
    sorted_z = np.sort(z)[::-1]
    cumulative_density = np.cumsum(sorted_z) / np.sum(sorted_z)
    credible_intervals = [0.6827, 0.9545, 0.9973]
    threshold_indexes = np.searchsorted(cumulative_density, credible_intervals)
    thresholds = sorted_z[threshold_indexes]
    thresholds = thresholds[::-1]
    thresholds = np.concatenate([thresholds, np.array([np.max(sorted_z)])])
    alpha_interval = 1 / (len(threshold_indexes) + 1)
    alphas = [alpha_interval * (credible_interval_index + 1)
              for credible_interval_index in range(len(credible_intervals))]
    figure_.contour(x=x_meshgrid, y=y_meshgrid, z=z_meshgrid, levels=thresholds,
                    fill_color=color, fill_alpha=alphas)


def create_1d_kde_credible_interval_figure(array: npt.NDArray) -> figure:
    figure_ = figure()
    add_1d_kde_credible_interval_to_figure(figure_, array)
    return figure_


def create_multi_distribution_1d_kde_credible_interval_figure(arrays: list[npt.NDArray]) -> figure:
    figure_ = figure()
    colors = [mediumblue, firebrick]
    for array, color in zip(arrays, colors):
        add_1d_kde_credible_interval_to_figure(figure_, array, color=color)
    return figure_


def add_1d_histogram_credible_interval_to_figure(figure_: figure, array: npt.NDArray, color: Color):
    histogram_values, histogram_edges = np.histogram(array, bins=60, density=True)
    histogram_centers = (histogram_edges[1:] + histogram_edges[:-1]) / 2
    add_1d_credible_interval_contour_to_figure(figure_, histogram_centers, histogram_values, color)


def create_multi_distribution_1d_histogram_credible_interval_figure(arrays: list[npt.NDArray]) -> figure:
    figure_ = figure()
    colors = [mediumblue, firebrick]
    for array, color in zip(arrays, colors):
        add_1d_histogram_credible_interval_to_figure(figure_, array, color)
    return figure_


def create_1d_histogram_credible_interval_figure(
        array: npt.NDArray,
        *,
        color: Color = mediumblue
) -> figure:
    figure_ = figure()
    add_1d_histogram_credible_interval_to_figure(figure_, array, color)
    return figure_


def create_multi_distribution_2d_kde_credible_interval_figure(
        array_pairs: list[tuple[npt.NDArray, npt.NDArray]]) -> figure:
    figure_ = figure()
    colors = [mediumblue, firebrick]
    for array_pair, color in zip(array_pairs, colors):
        add_2d_kde_credible_interval_to_figure(figure_, *array_pair, color=color)
    return figure_


def create_multi_distribution_2d_histogram_figure(
        array_pairs: list[tuple[npt.NDArray, npt.NDArray]]) -> figure:
    figure_ = figure()
    colors = [mediumblue, firebrick]
    for array_pair, color in zip(array_pairs, colors):
        add_2d_histogram_to_figure(figure_, *array_pair, color=color)
    return figure_


def create_multi_distribution_2d_histogram_credible_interval_contour_figure(
        array_pairs: list[tuple[npt.NDArray, npt.NDArray]]) -> figure:
    figure_ = figure()
    colors = [mediumblue, firebrick]
    for array_pair, color in zip(array_pairs, colors):
        add_2d_histogram_credible_interval_contour_to_figure(figure_, *array_pair, color=color)
    return figure_


def create_2d_histogram_credible_interval_contour_figure(
        array0: npt.NDArray,
        array1: npt.NDArray,
        *,
        color: Color = mediumblue
) -> figure:
    figure_ = figure()
    add_2d_histogram_credible_interval_contour_to_figure(figure_, array0, array1, color=color)
    return figure_


def add_2d_histogram_to_figure(
        figure_: figure,
        array0: npt.NDArray,
        array1: npt.NDArray,
        *,
        color: Color = mediumblue,
):
    histogram_values, histogram_edges0, histogram_edges1 = np.histogram2d(array0, array1, bins=30, density=True)
    histogram_maximum = np.max(histogram_values)
    histogram_normalized = histogram_values / histogram_maximum
    image_width = histogram_edges0[-1] - histogram_edges0[0]
    image_height = histogram_edges1[-1] - histogram_edges1[0]
    image_anchor0 = histogram_edges0[0]
    image_anchor1 = histogram_edges1[0]
    palette = varying_alpha_palette(color.to_rgb().to_hex())
    figure_.image(image=[np.transpose(histogram_normalized)], x=image_anchor0, y=image_anchor1, dw=image_width,
                  dh=image_height, palette=palette)


def add_2d_histogram_credible_interval_contour_to_figure(
        figure_: figure,
        array0: npt.NDArray,
        array1: npt.NDArray,
        *,
        color: Color = mediumblue,
):
    histogram_values, histogram_edges0, histogram_edges1 = np.histogram2d(array0, array1, bins=[30, 40], density=True)
    histogram_centers0 = (histogram_edges0[1:] + histogram_edges0[:-1]) / 2
    histogram_centers1 = (histogram_edges1[1:] + histogram_edges1[:-1]) / 2
    x_meshgrid, y_meshgrid = np.meshgrid(histogram_centers0, histogram_centers1)
    z_meshgrid = np.transpose(histogram_values)
    add_contour_to_figure(figure_, x_meshgrid, y_meshgrid, z_meshgrid, color)


def add_1d_kde_credible_interval_to_figure(
        figure_: figure,
        array: npt.NDArray,
        *,
        color: Color = mediumblue,
):
    kde = stats.gaussian_kde(array)
    distribution_plotting_range = get_padded_range_for_array(array)
    # Evaluate the KDE on a grid
    plotting_positions = np.linspace(*distribution_plotting_range, 1000)
    distribution_values = kde(plotting_positions)
    add_1d_credible_interval_contour_to_figure(figure_, plotting_positions, distribution_values, color)


def add_1d_credible_interval_contour_to_figure(figure_, distribution_positions, distribution_values, color):
    credible_interval_thresholds = np.array([0.6827, 0.9545, 0.9973])
    plotting_position_threshold_indexes = get_indexes_for_thresholds(credible_interval_thresholds,
                                                                     distribution_positions, distribution_values)
    interval_segment_plotting_positions_array, interval_segment_values_array = create_segments_for_indexes(
        plotting_position_threshold_indexes, distribution_positions, distribution_values)
    alpha_interval = 1 / (len(credible_interval_thresholds) + 1)
    for credible_interval_threshold_index in range(len(credible_interval_thresholds)):
        lower_segment_positions = interval_segment_plotting_positions_array[credible_interval_threshold_index + 1]
        upper_segment_positions = interval_segment_plotting_positions_array[-(credible_interval_threshold_index + 2)]
        lower_segment_values = interval_segment_values_array[credible_interval_threshold_index + 1]
        upper_segment_values = interval_segment_values_array[-(credible_interval_threshold_index + 2)]
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
        alpha = alpha_interval * (credible_interval_threshold_index + 1)
        lower_band = Band(source=lower_column_data_source, base='base', lower='lower', upper='upper',
                          fill_color=color, fill_alpha=alpha)
        upper_band = Band(source=upper_column_data_source, base='base', lower='lower', upper='upper',
                          fill_color=color, fill_alpha=alpha)
        figure_.add_layout(lower_band)
        figure_.add_layout(upper_band)
    median_position_index = plotting_position_threshold_indexes[
        math.floor(plotting_position_threshold_indexes.shape[0] / 2)]
    median_value = distribution_values[median_position_index]
    median_position = distribution_positions[median_position_index]
    figure_.line(x=[median_position, median_position], y=[0, median_value], color=color)
    figure_.line(x=distribution_positions, y=distribution_values, color=color)


def create_segments_for_indexes(
        plotting_position_threshold_indexes: npt.NDArray,
        distribution_positions: npt.NDArray,
        distribution_values: npt.NDArray
) -> (npt.NDArray, npt.NDArray):
    interval_segment_plotting_positions_array = np.split(distribution_positions, plotting_position_threshold_indexes)
    interval_segment_values_array = np.split(distribution_values, plotting_position_threshold_indexes)
    # Fill the gaps between intervals.
    for split_index in reversed(range(len(interval_segment_plotting_positions_array) - 1)):
        interval_segment_plotting_positions_array[split_index] = np.append(
            interval_segment_plotting_positions_array[split_index],
            interval_segment_plotting_positions_array[split_index + 1][0]
        )
        interval_segment_values_array[split_index] = np.append(
            interval_segment_values_array[split_index],
            interval_segment_values_array[split_index + 1][0]
        )
    return interval_segment_plotting_positions_array, interval_segment_values_array


def get_indexes_for_thresholds(credible_interval_thresholds, distribution_positions, distribution_values):
    half_credible_interval_thresholds = credible_interval_thresholds / 2
    quantile_thresholds = np.concatenate([
        0.5 - half_credible_interval_thresholds[::-1],  # The lower bounds of the intervals.
        np.array([0.5]),  # The median.
        0.5 + half_credible_interval_thresholds,  # The upper bounds of the intervals.
    ])
    threshold_values = np.quantile(distribution_positions, quantile_thresholds, weights=distribution_values,
                                   method='inverted_cdf')
    plotting_position_threshold_indexes = np.searchsorted(distribution_positions, threshold_values)
    return plotting_position_threshold_indexes


def get_range_1d_for_array(array: npt.NDArray, padding_fraction: float = 0.05) -> Range1d:
    range_start, range_end = get_padded_range_for_array(array, padding_fraction)
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
            Concatenate[npt.NDArray, P], figure] = create_1d_histogram_credible_interval_figure,
        marginal_2d_figure_function: Callable[
            Concatenate[
                npt.NDArray, npt.NDArray, P], figure] = create_2d_histogram_credible_interval_contour_figure,
        labels: list[str] | None = None,
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
                logger.info(f'Creating 1D marginal figure for row {row_index}, column {column_index}.')
                figure_ = marginal_1d_figure_function(marginal_1d_array, **sub_figure_kwargs)
            if row_index > column_index:  # 2D marginal distribution figures.
                marginal_2d_array0 = array[:, column_index]
                marginal_2d_array1 = array[:, row_index]
                logger.info(f'Creating 2D marginal figure for row {row_index}, column {column_index}.')
                figure_ = marginal_2d_figure_function(marginal_2d_array0, marginal_2d_array1, **sub_figure_kwargs)
            if figure_ is not None:
                compose_figure_for_corner_plot_position(figure_, column_index, row_index, number_of_parameters, labels,
                                                        x_ranges, y_ranges, toolbar, subfigure_size,
                                                        subfigure_min_border, end_axis_minimum_border)
                row_figures.append(figure_)
        plots.append(row_figures)

    # Create a grid plot
    layout_ = layout(*plots)

    # Display the plot
    show(layout_)


def create_multi_distribution_corner_plot(
        arrays: list[npt.NDArray],
        *,
        marginal_1d_figure_function: Callable[
            Concatenate[
                list[npt.NDArray], P], figure] = create_multi_distribution_1d_histogram_credible_interval_figure,
        marginal_2d_figure_function: Callable[
            Concatenate[list[tuple[npt.NDArray, npt.NDArray]], P], figure
        ] = create_multi_distribution_2d_histogram_credible_interval_contour_figure,
        labels: list[str] | None = None,
        subfigure_size: int = 200,
        subfigure_min_border: int = 5,
        end_axis_minimum_border: int = 100,
        sub_figure_kwargs: dict[Any, Any] = None
) -> Column:
    if sub_figure_kwargs is None:
        sub_figure_kwargs = {}

    number_of_dimensions = arrays[0].shape[1]
    for array in arrays:
        assert len(array.shape) == 2
        assert array.shape[1] == number_of_dimensions

    if labels is not None and len(labels) != number_of_dimensions:
        raise ValueError('`labels` must be the same length as the number of dimensions.')

    # Prepare shared components.
    concatenated_array = np.concatenate(arrays, axis=0)
    x_ranges = [get_range_1d_for_array(concatenated_array[:, index])
                for index in range(number_of_dimensions)]
    y_ranges = [get_range_1d_for_array(concatenated_array[:, index])
                for index in range(number_of_dimensions)]
    tools = [PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool()]
    toolbar = Toolbar(tools=tools)

    plots = []

    for row_index in range(number_of_dimensions):
        row_figures: list[figure] = []
        for column_index in range(number_of_dimensions):
            figure_ = None
            if row_index == column_index:  # 1D marginal distribution figures.
                marginal_1d_arrays = [array[:, row_index] for array in arrays]
                logger.info(f'Creating 1D marginal figure for row {row_index}, column {column_index}.')
                figure_ = marginal_1d_figure_function(marginal_1d_arrays, **sub_figure_kwargs)
            if row_index > column_index:  # 2D marginal distribution figures.
                marginal_2d_array_pairs = [(array[:, column_index], array[:, row_index]) for array in arrays]
                logger.info(f'Creating 2D marginal figure for row {row_index}, column {column_index}.')
                figure_ = marginal_2d_figure_function(marginal_2d_array_pairs, **sub_figure_kwargs)
            if figure_ is not None:
                compose_figure_for_corner_plot_position(figure_, column_index, row_index, number_of_dimensions, labels,
                                                        x_ranges, y_ranges, toolbar, subfigure_size,
                                                        subfigure_min_border, end_axis_minimum_border)
                row_figures.append(figure_)
        plots.append(row_figures)

    # Create a grid plot
    layout_ = layout(*plots)

    return layout_


def compose_figure_for_corner_plot_position(figure_: figure, column_index: int, row_index: int,
                                            number_of_dimensions: int, labels: list[str] | None,
                                            x_ranges: list[Range1d], y_ranges: list[Range1d], toolbar: Toolbar,
                                            subfigure_size: int, subfigure_min_border: int,
                                            end_axis_minimum_border: int):
    if labels is None:
        labels = [None] * number_of_dimensions
    if row_index == column_index:  # 1D marginal distribution figures.
        if len(figure_.left) > 0:
            axis = figure_.left.pop(0)
            figure_.add_layout(axis, Place.right)
        figure_.min_border = subfigure_min_border
        if column_index == 0:
            figure_.min_border_left = end_axis_minimum_border
    if row_index > column_index:  # 2D marginal distribution figures.
        figure_.min_border = subfigure_min_border
        if column_index == 0:
            figure_.min_border_left = end_axis_minimum_border
            figure_.yaxis.axis_label = labels[row_index]
        else:
            figure_.yaxis.visible = False
        figure_.y_range = y_ranges[row_index]
    if row_index == number_of_dimensions - 1:
        figure_.min_border_bottom = end_axis_minimum_border
        figure_.xaxis.axis_label = labels[column_index]
        figure_.xaxis.major_label_orientation = math.tau / 8
    else:
        figure_.xaxis.visible = False
    if row_index == number_of_dimensions - 1 and column_index == number_of_dimensions - 1:
        figure_.toolbar_location = Place.below
    else:
        figure_.toolbar_location = None
    figure_.frame_width = subfigure_size
    figure_.frame_height = subfigure_size
    figure_.x_range = x_ranges[column_index]
    figure_.toolbar = toolbar
