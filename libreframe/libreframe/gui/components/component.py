from abc import ABCMeta, abstractmethod

from PIL import Image


class Component(metaclass=ABCMeta):

    def __init__(self, name: str, cell_x: int = 12, cell_y: int = 12) -> None:
        self._name = name
        self._cell_x = cell_x
        self._cell_y = cell_y

    @property
    def name(self) -> str:
        return self._name

    @property
    def cell_x(self) -> int:
        return self._cell_x

    @property
    def cell_y(self) -> int:
        return self._cell_y

    @abstractmethod
    def draw(self, cell_width: int, cell_height: int) -> Image:
        raise NotImplementedError
