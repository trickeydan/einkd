from abc import ABCMeta, abstractmethod

from PIL import Image

from libreframe.gui.window import Window


class Display(metaclass=ABCMeta):

    def display(self, window: Window) -> None:
        image = window.draw()
        self.draw(image.convert(self.colour_mode))

    @abstractmethod
    def draw(self, image: Image) -> None:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @property
    def colour_mode(self) -> str:
        return "RGB"

    def __enter__(self) -> 'Display':
        self.start()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.stop()
