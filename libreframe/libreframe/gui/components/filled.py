from PIL import Image

from .component import Component


class FilledComponent(Component):

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

    def draw(self, cell_width: int, cell_height: int) -> Image:
        return Image.new(
            "RGB",
            (cell_width * self.cell_x, cell_height * self.cell_y),
            self._colour,
        )
