"""GUI Window."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from PIL import Image

from .components import Component


@dataclass
class Window:
    """GUI Window."""

    width: int
    height: int
    grid_width: int = 12
    grid_height: int = 12
    components: Dict[Tuple[int, int], Component] = field(default_factory=dict)

    @property
    def cell_width(self) -> int:
        """
        The width of a single cell.

        :returns: The width of a cell in pixels.
        """
        return self.width // self.grid_width

    @property
    def cell_height(self) -> int:
        """
        The height of a single cell.

        :returns: The height of a cell in pixels.
        """
        return self.height // self.grid_height

    def validate_components(self) -> None:
        """Validate the components in the window."""
        # Check component names are unique
        if len({c.name for c in self.components.values()}) != len(self.components):
            raise ValueError("Component names must be unique")

        cells: List[List[Optional[Tuple[int, int]]]] = [
            [None for _ in range(self.grid_height)]
            for _ in range(self.grid_width)
        ]

        # Check for overlaps
        for (x_base, y_base), component in self.components.items():
            for x_offset in range(component.cell_x):
                x = x_base + x_offset
                for y_offset in range(component.cell_y):
                    y = y_base + y_offset
                    val = cells[x][y]

                    if val is not None:
                        overlapping_component = self.components[val]
                        raise ValueError(
                            f"Component {component.name} overlaps"
                            f" {overlapping_component.name}",
                        )

                    cells[x][y] = (x_base, y_base)

    def draw(self) -> Image.Image:
        """
        Render the window.

        Validate and render all components.

        :returns: A renders PIL Image object.
        """
        self.validate_components()
        image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        x_offset = (self.width % self.cell_width) // 2
        y_offset = (self.height % self.cell_height) // 2
        for (x, y), comp in self.components.items():
            sub_image = comp.draw(self.cell_width, self.cell_height)
            image.paste(
                sub_image,
                (
                    x_offset + x * self.cell_width,
                    y_offset + y * self.cell_height,
                ),
            )
        return image
