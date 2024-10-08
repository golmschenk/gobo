from typing import Iterable

from bokeh.colors import Color
from bokeh.colors.named import mediumblue, firebrick, goldenrod, forestgreen, mediumorchid


class DefaultDiscretePalette:
    def __init__(self):
        self.blue = mediumblue
        self.red = firebrick
        self.yellow = goldenrod
        self.green = forestgreen
        self.purple = mediumorchid
        self.colors = [self.blue, self.red, self.yellow, self.green, self.purple]

    def __getitem__(self, item: int) -> Color:
        return self.colors[item]

    def __iter__(self) -> Iterable[Color]:
        return iter(self.colors)


default_discrete_palette = DefaultDiscretePalette()
