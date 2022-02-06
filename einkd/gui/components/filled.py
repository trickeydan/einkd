"""A component that fills an area with solid colour."""
from PIL import Image

from .component import Component


class FilledComponent(Component):
    """A component that fills an area with solid colour."""

    def __init__(
        self,
        name: str,
        cell_x: int = 12,
        cell_y: int = 12,
        *,
        colour: str,
    ) -> None:
        super().__init__(name, cell_x, cell_y)
        self._colour = colour

    def draw(self, cell_width: int, cell_height: int) -> Image.Image:
        """
        Draw the component.

        :param cell_width: Width of the component in cells.
        :param cell_height: Heigh of the component in cells.
        :returns: A rendered component as a PIL image.
        """
        return Image.new(
            "RGB",
            (cell_width * self.cell_x, cell_height * self.cell_y),
            self._colour,
        )
