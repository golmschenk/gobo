import numpy as np


def remove_outliers(data: np.ndarray, median_deviation_rejection_factor: float = 4.4477) -> np.ndarray:
    """
    Remove outliers based on the median deviation from the median.

    :param data: The data to remove the outliers from.
    :param median_deviation_rejection_factor: The rejection factor. Data points are rejected if they are outside this
        value multiplied by the median deviation from the median. 4.4477 is 3 / 0.6745, which rejects above 3 standard
        deviations if the input data is a normal distribution.
    :return: The data with the outliers removed.
    """
    median = np.median(data)
    deviation_from_median = np.abs(data - median)
    median_deviation_from_median = np.median(deviation_from_median)
    if median_deviation_from_median == 0:
        return data[data == median]
    else:
        scaled_deviation_from_median = deviation_from_median / median_deviation_from_median
        return data[scaled_deviation_from_median < median_deviation_rejection_factor]
