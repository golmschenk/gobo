import logging
from typing import Self

import numpy as np
from bokeh.document import Document
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

from gobo.internal.corner_plot import create_multi_distribution_corner_plot

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
        random_generator = np.random.default_rng()
        array0 = random_generator.normal(loc=0.0, scale=1.0, size=[10000, 2])
        array1 = random_generator.normal(loc=0.5, scale=1.0, size=[10000, 2])
        corner_plot = create_multi_distribution_corner_plot([array0, array1])
        document.add_root(corner_plot)

    def run(self):
        apps = {'/': Application(FunctionHandler(self.add_to_document))}  # Put the app at the root address.
        server = Server(apps, port=DEFAULT_PORT)
        server.start()
        server.io_loop.add_callback(server.show, '/')  # Open the browser.
        server.io_loop.start()  # Control loop.


if __name__ == '__main__':
    explorer = PosteriorDistributionExplorer.new()
    explorer.run()
