"""A component that renders an image from a file."""
from pathlib import Path

from PIL import Image

from .component import Component


class ImageComponent(Component):
    """A component that renders an image from a file."""

    def __init__(
        self,
        name: str,
        cell_x: int = 12,
        cell_y: int = 12,
        *,
        image: Image.Image,
        centre: bool = True,
    ) -> None:
        super().__init__(name, cell_x, cell_y)
        self.image = image
        self._centre = centre

    def draw(self, cell_width: int, cell_height: int) -> Image.Image:
        """
        Draw the component.

        :param cell_width: Width of the component in cells.
        :param cell_height: Heigh of the component in cells.
        :returns: A rendered component as a PIL image.
        """
        image = self.image.convert("RGBA")
        dimensions = (cell_width * self.cell_x, cell_height * self.cell_y)
        canvas = Image.new(
            "RGB",
            dimensions,
            (255, 255, 255),
        )

        image.thumbnail(dimensions)

        if self._centre:
            draw_at = (
                abs(image.size[0] - dimensions[0]) // 2,
                abs(image.size[1] - dimensions[1]) // 2,
            )
        else:
            draw_at = (0, 0)

        canvas.paste(image, draw_at, mask=image)
        return canvas
