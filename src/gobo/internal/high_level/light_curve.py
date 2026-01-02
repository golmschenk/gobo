import numpy.typing as npt
from bokeh.io import show
from bokeh.plotting import figure

from gobo.internal.palette import default_discrete_palette


def create_light_curve_figure(times: npt.NDArray, fluxes: npt.NDArray) -> figure:
    light_curve_figure = figure(x_axis_label='Time', y_axis_label='Flux')
    light_curve_figure.scatter(x=times, y=fluxes, line_color=default_discrete_palette.blue, line_alpha=0.7,
                               fill_color=default_discrete_palette.blue, fill_alpha=0.5)
    light_curve_figure.line(x=times, y=fluxes, line_alpha=0.2, line_color=default_discrete_palette.blue)
    return light_curve_figure


def show_light_curve(times: npt.NDArray, fluxes: npt.NDArray) -> None:
    light_curve_figure = create_light_curve_figure(times, fluxes)
    show(light_curve_figure)
