import numpy as np

from gobo.range import remove_outliers


def test_remove_outliers():
    data = np.array([-1, 2, -2, 1, 100])

    data_with_outliers_removed = remove_outliers(data)

    assert np.array_equal(data_with_outliers_removed, np.array([-1, 2, -2, 1]))
