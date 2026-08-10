import math

import numpy as np
from bokeh.colors import Color
from bokeh.models import ColumnDataSource, Band
from bokeh.plotting import figure
import numpy.typing as npt

from gobo.internal.palette import default_discrete_palette


def add_1d_histogram_credible_interval_contour_to_figure(
        figure_: figure,
        source: ColumnDataSource,
        x_column_name: str,
        color: Color,
        *,
        credible_intervals: npt.NDArray | None = None,
        alphas: npt.NDArray | None = None
):
    if credible_intervals is None:
        credible_intervals = [0.6827, 0.9545, 0.9973]  # Equivalent of 1,2,3-sigma for 1D standard deviations.
    if alphas is None:
        alpha_interval = 1 / (len(credible_intervals) + 1)
        alphas = [alpha_interval * (credible_interval_index + 1)
                  for credible_interval_index in range(len(credible_intervals))][::-1]
    else:
        if len(alphas) != len(credible_intervals):
            raise ValueError(f'The number of alphas passed ({len(alphas)} passed) must match the number of credible '
                             f'intervals ({len(credible_intervals)} passed).')
    histogram_values, histogram_edges = np.histogram(source.data[x_column_name], bins=60, density=True)
    histogram_centers = (histogram_edges[1:] + histogram_edges[:-1]) / 2
    alphas = np.array([0.5, 0.3, 0.1])  # TODO: Why is this here? Probably just looks better then the above math driven thing?
    alphas_in_interval_order = alphas[::-1]
    credible_interval_thresholds = credible_intervals
    plotting_position_threshold_indexes = get_indexes_for_thresholds(credible_interval_thresholds,
                                                                     histogram_centers, histogram_values)
    interval_segment_plotting_positions_array, interval_segment_values_array = create_segments_for_indexes(
        plotting_position_threshold_indexes, histogram_centers, histogram_values)
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
        lower_band = Band(source=lower_column_data_source, base='base', lower='lower', upper='upper',
                          fill_color=color, fill_alpha=alphas_in_interval_order[credible_interval_threshold_index])
        upper_band = Band(source=upper_column_data_source, base='base', lower='lower', upper='upper',
                          fill_color=color, fill_alpha=alphas_in_interval_order[credible_interval_threshold_index])
        figure_.add_layout(lower_band)
        figure_.add_layout(upper_band)
    median_position_index = plotting_position_threshold_indexes[
        math.floor(plotting_position_threshold_indexes.shape[0] / 2)]
    median_value = histogram_values[median_position_index]
    median_position = histogram_centers[median_position_index]
    figure_.line(x=[median_position, median_position], y=[0, median_value], color=color)
    figure_.line(x=histogram_centers, y=histogram_values, color=color)


def get_indexes_for_thresholds(credible_interval_thresholds, distribution_positions, distribution_values):
    if isinstance(credible_interval_thresholds, list):
        credible_interval_thresholds = np.array(credible_interval_thresholds)
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


def create_segments_for_indexes(
        plotting_position_threshold_indexes: npt.NDArray,
        distribution_positions: npt.NDArray,
        distribution_values: npt.NDArray
) -> tuple[npt.NDArray, npt.NDArray]:
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


def add_2d_histogram_credible_interval_contour_to_figure(
        figure_: figure,
        source: ColumnDataSource,
        x_column_name: str,
        y_column_name: str,
        color: Color = default_discrete_palette.blue,
        *,
        credible_intervals: npt.NDArray | None = None,
        alphas: npt.NDArray | None = None
):
    if credible_intervals is None:
        credible_intervals = [0.39346934, 0.86466472, 0.988891]  # Equivalent of 1,2,3-sigma for 2D standard deviations.
    if alphas is None:
        alpha_interval = 1 / (len(credible_intervals) + 1)
        alphas = [alpha_interval * (credible_interval_index + 1)
                  for credible_interval_index in range(len(credible_intervals))][::-1]
    else:
        if len(alphas) != len(credible_intervals):
            raise ValueError(f'The number of alphas passed ({len(alphas)} passed) must match the number of credible '
                             f'intervals ({len(credible_intervals)} passed).')
    histogram_values, histogram_edges0, histogram_edges1 = np.histogram2d(
        source.data[x_column_name], source.data[y_column_name], bins=[30, 30], density=True)
    histogram_centers0 = (histogram_edges0[1:] + histogram_edges0[:-1]) / 2
    histogram_centers1 = (histogram_edges1[1:] + histogram_edges1[:-1]) / 2
    x_meshgrid, y_meshgrid = np.meshgrid(histogram_centers0, histogram_centers1)
    z_meshgrid = np.transpose(histogram_values)
    add_2d_contour_to_figure(figure_, x_meshgrid, y_meshgrid, z_meshgrid, color, credible_intervals, alphas)


def add_2d_contour_to_figure(figure_: figure, x_meshgrid, y_meshgrid, z_meshgrid, color: Color,
                             credible_intervals: npt.NDArray, alphas: npt.NDArray):
    z = z_meshgrid.ravel()
    sorted_z = np.sort(z)[::-1]
    cumulative_density = np.cumsum(sorted_z) / np.sum(sorted_z)
    threshold_indexes = np.searchsorted(cumulative_density, credible_intervals)
    thresholds = sorted_z[threshold_indexes]
    thresholds = thresholds[::-1]
    thresholds = np.concatenate([thresholds, np.array([np.max(sorted_z)])])
    alphas = alphas[::-1]
    figure_.contour(x=x_meshgrid, y=y_meshgrid, z=z_meshgrid, levels=thresholds,
                    fill_color=color, fill_alpha=alphas)