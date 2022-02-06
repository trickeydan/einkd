"""A component in the GUI."""
from abc import ABCMeta, abstractmethod

from PIL import Image


class Component(metaclass=ABCMeta):
    """A component in the GUI."""

    def __init__(self, name: str, cell_x: int = 12, cell_y: int = 12) -> None:
        self._name = name
        self._cell_x = cell_x
        self._cell_y = cell_y

    @property
    def name(self) -> str:
        """
        The name of a component.

        :returns: The name of the component.
        """
        return self._name

    @property
    def cell_x(self) -> int:
        """
        X position of the cell.

        :returns: X position of the cell.
        """
        return self._cell_x

    @property
    def cell_y(self) -> int:
        """
        Y position of the cell.

        :returns: Y position of the cell.
        """
        return self._cell_y

    @abstractmethod
    def draw(self, cell_width: int, cell_height: int) -> Image.Image:
        """
        Draw the component.

        :param cell_width: Width of the component in cells.
        :param cell_height: Heigh of the component in cells.
        :returns: A rendered component as a PIL image.
        """
        raise NotImplementedError
