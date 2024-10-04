import numpy as np

from gobo.internal.corner_plot import create_segments_for_indexes


def test_create_segments_for_indexes_handles_empty_segments():
    indexes = np.array([0, 3, 3, 3])
    distribution_positions = np.array([0, 10, 20, 30])
    distribution_values = np.array([0, 100, 200, 300])

    interval_segment_plotting_positions_array, interval_segment_values_array = create_segments_for_indexes(
        indexes, distribution_positions, distribution_values)

    assert all([interval_segment_plotting_positions.shape[0] > 0
                for interval_segment_plotting_positions in interval_segment_plotting_positions_array])
    assert all([interval_segment_values.shape[0] > 0
                for interval_segment_values in interval_segment_values_array])
