from PIL import Image, ImageDraw

from .component import Component


class TextComponent(Component):

    def __init__(
        self,
        name: str,
        cell_x: int = 12,
        cell_y: int = 12,
        *,
        text: str,
        background_colour: str = "white"
    ) -> None:
        super().__init__(name, cell_x, cell_y)
        self._text = text
        self._background_colour = background_colour

    def draw(self, cell_width: int, cell_height: int) -> Image:
        image = Image.new(
            "RGB",
            (cell_width * self.cell_x, cell_height * self.cell_y),
            self._background_colour,
        )
        d = ImageDraw.Draw(image)
        d.text((0,0), self._text, fill="black")
        return image