import numpy as np
from bokeh.models import Range1d
from bokeh.plotting import figure, show
from bokeh.layouts import layout


def create_scatter_corner_plot(array):
    assert len(array.shape) == 2

    # Prepare shared ranges for the scatter plots.
    x_ranges = [Range1d(start=np.min(array[:, j]), end=np.max(array[:, j])) for j in range(array.shape[1])]
    y_ranges = [Range1d(start=np.min(array[:, i]), end=np.max(array[:, i])) for i in range(array.shape[1])]

    plots = []

    for row_index in range(array.shape[1]):
        row_figures: list[figure] = []
        for column_index in range(array.shape[1]):
            figure_ = None
            subfigure_size = 200
            end_axis_minimum_border = 100
            subfigure_min_border = 5
            # Marginal distribution histogram subfigures.
            if row_index == column_index:
                figure_ = figure(width=subfigure_size, height=subfigure_size, toolbar_location=None,
                                 x_range=x_ranges[column_index], y_axis_location="right", x_axis_type=None)
                figure_.min_border = subfigure_min_border
                hist, edges = np.histogram(array[:, row_index], density=True, bins=30)
                figure_.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
                figure_.xaxis.visible = False
                figure_.yaxis.visible = True
                if column_index == 0:
                    figure_.min_border_left = end_axis_minimum_border
            # Parameter comparisons.
            elif row_index > column_index:
                figure_ = figure(width=subfigure_size, height=subfigure_size, toolbar_location=None,
                                 x_range=x_ranges[column_index], y_range=y_ranges[row_index])
                figure_.min_border = subfigure_min_border
                figure_.scatter(array[:, column_index], array[:, row_index], size=3, alpha=0.5)
                if column_index == 0:
                    figure_.min_border_left = end_axis_minimum_border
                else:
                    figure_.yaxis.visible = False
                if row_index == array.shape[1] - 1:
                    figure_.min_border_bottom = end_axis_minimum_border
                else:
                    figure_.xaxis.visible = False
            if figure_ is not None:
                figure_.frame_width = subfigure_size
                figure_.frame_height = subfigure_size
                figure_.xgrid.grid_line_color = None
                figure_.ygrid.grid_line_color = None
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
    create_scatter_corner_plot(data_)
