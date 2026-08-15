import logging
from typing import Self

import numpy as np
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.document import Document
from bokeh.models.sources import ColumnDataSource
from bokeh.server.server import Server

from gobo.internal.corner_plot_new.corner_plot_revised import CornerPlot

DEFAULT_PORT = 28194

logger = logging.getLogger(__name__)


class PosteriorDistributionExplorer:
    def __init__(self):
        pass

    @classmethod
    def new(cls) -> Self:
        return cls()

    @staticmethod
    def add_to_document(document: Document) -> None:
        sources = PosteriorDistributionExplorer.create_example_distribution_sources()
        corner_plot = CornerPlot.new(sources)
        document.add_root(corner_plot)

    @staticmethod
    def create_example_distribution_sources() -> list[ColumnDataSource]:
        random_generator = np.random.default_rng()
        array0_part0 = random_generator.normal(loc=0.0, scale=1.0, size=[5000, 4])
        array0_part1 = random_generator.normal(loc=-2.0, scale=1.0, size=[5000, 4])
        array0 = np.concatenate([array0_part0, array0_part1], axis=0)
        array1_part0 = random_generator.normal(loc=0.5, scale=1.0, size=[5000, 4])
        array1_part1 = random_generator.normal(loc=1.0, scale=1.0, size=[5000, 4])
        array1 = np.concatenate([array1_part0, array1_part1], axis=0)
        parameter_names = ['a', 'b', 'c', 'd']
        source0 = ColumnDataSource({parameter_name: array0[:, i] for i, parameter_name in enumerate(parameter_names)})
        source1 = ColumnDataSource({parameter_name: array1[:, i] for i, parameter_name in enumerate(parameter_names)})
        return [source0, source1]

    def run(self):
        apps = {'/': Application(FunctionHandler(self.add_to_document))}  # Put the app at the root address.
        server = Server(apps, port=DEFAULT_PORT)
        server.start()
        server.io_loop.add_callback(server.show, '/')  # Open the browser.
        server.io_loop.start()  # Control loop.


if __name__ == '__main__':
    explorer = PosteriorDistributionExplorer.new()
    explorer.run()
