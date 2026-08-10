import logging
import math
from typing import ParamSpec, Callable, Self, Iterable

import numpy as np
from bokeh.colors import Color
from bokeh.core.enums import Place
from bokeh.models import Column, PanTool, WheelZoomTool, BoxZoomTool, ResetTool, Toolbar, Row
from bokeh.models.ranges import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure

from gobo.internal.corner_plot_new.corner_plot_subfigure_plotting import \
    add_1d_histogram_credible_interval_contour_to_figure, add_2d_histogram_credible_interval_contour_to_figure
from gobo.internal.palette import default_discrete_palette

P = ParamSpec('P')

logger = logging.getLogger(__name__)


class CornerPlot(Column):
    __implementation__ = 'corner_plot_revised.ts'

    @classmethod
    def new(
            cls,
            distribution_sources: list[ColumnDataSource],
            *,
            marginal_1d_plotting_function: Callable[[figure, ColumnDataSource, str, Color
                                                     ], None] = add_1d_histogram_credible_interval_contour_to_figure,
            marginal_2d_plotting_function: Callable[[figure, ColumnDataSource, str, str, Color
                                                     ], None] = add_2d_histogram_credible_interval_contour_to_figure,
            marginal_1d_figure_constructor_function: Callable[[], figure] = figure,
            marginal_2d_figure_constructor_function: Callable[[], figure] = figure,
            colors: Iterable[Color] = default_discrete_palette,
            subfigure_size: int = 200,
            subfigure_min_border: int = 5,
            end_axis_minimum_border: int = 100,
    ) -> Self:
        parameter_names = [parameter_name for source in distribution_sources for parameter_name in source.column_names]
        sorted_unique_parameter_names, unique_parameter_name_indexes = np.unique(parameter_names, return_index=True)
        parameter_names = sorted_unique_parameter_names[np.argsort(unique_parameter_name_indexes)]
        x_range_dictionary = {parameter_name: Range1d() for parameter_name in parameter_names}
        y_range_dictionary = {parameter_name: Range1d() for parameter_name in parameter_names}
        figure_dictionary: dict[str, dict[str, figure]] = {}
        for row_index, row_parameter_name in enumerate(parameter_names):
            row_figure_dictionary: dict[str, figure] = {}
            for column_index, column_parameter_name in enumerate(parameter_names):
                figure_ = None
                if row_parameter_name == column_parameter_name:  # 1D marginal distribution figures.
                    logger.info(f'Creating 1D marginal figure for row {row_parameter_name}, '
                                f'column {column_parameter_name}.')
                    figure_ = marginal_1d_figure_constructor_function()
                    for distribution_source, color in zip(distribution_sources, colors):
                        marginal_1d_plotting_function(figure_, distribution_source, column_parameter_name, color)
                if row_index > column_index:  # 2D marginal distribution figures.
                    logger.info(f'Creating 2D marginal figure for row {row_index}, column {column_index}.')
                    figure_ = marginal_2d_figure_constructor_function()
                    for distribution_source, color in zip(distribution_sources, colors):
                        marginal_2d_plotting_function(figure_, distribution_source, column_parameter_name,
                                                      row_parameter_name, color)
                if figure_ is not None:
                    cls.compose_figure_for_corner_plot_position(
                        figure_, len(parameter_names), column_index, row_index, column_parameter_name,
                        row_parameter_name, x_range_dictionary[column_parameter_name],
                        y_range_dictionary[row_parameter_name], subfigure_size, subfigure_min_border,
                        end_axis_minimum_border)
                    row_figure_dictionary[column_parameter_name] = figure_
            figure_dictionary[row_parameter_name] = row_figure_dictionary
        rows = [Row(children=[figure_ for figure_ in row_figure_dictionary.values()])
                for row_figure_dictionary in figure_dictionary.values()]
        instance = cls(children=rows)
        return instance

    def __init__(self, children: list[Row]):
        super().__init__(children=children)


    @staticmethod
    def compose_figure_for_corner_plot_position(figure_: figure, number_of_parameters: int,
                                                column_index: int, row_index: int,
                                                column_parameter_name: str, row_parameter_name: str,
                                                column_range: Range1d, row_range: Range1d,
                                                subfigure_size: int, subfigure_min_border: int,
                                                end_axis_minimum_border: int):
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
                figure_.yaxis.axis_label = row_parameter_name
            else:
                figure_.yaxis.visible = False
            figure_.y_range = row_range
        if row_index == number_of_parameters - 1:
            figure_.min_border_bottom = end_axis_minimum_border
            figure_.xaxis.axis_label = column_parameter_name
            figure_.xaxis.major_label_orientation = math.tau / 8
        else:
            figure_.xaxis.visible = False
        if row_index == number_of_parameters - 1 and column_index == number_of_parameters - 1:
            figure_.toolbar_location = Place.below
        else:
            figure_.toolbar_location = None
        figure_.frame_width = subfigure_size
        figure_.frame_height = subfigure_size
        figure_.x_range = column_range
        tools = [PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool()]
        toolbar = Toolbar(tools=tools)
        figure_.toolbar = toolbar
