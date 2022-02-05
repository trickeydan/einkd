"""Base classes for e-ink display drivers."""
from abc import ABCMeta, abstractmethod
from types import TracebackType
from typing import Optional, Type

from einkd.display import Display


class BaseDriver(metaclass=ABCMeta):
    """Base class for Eink Drivers."""

    _display: Optional[Display] = None

    @abstractmethod
    def setup(self) -> None:
        """
        Set up the display.

        After this method has been run, _display should exist.

        This should fail if the display has already been setup.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up the display.

        After this method has been run, _display should be None.
        """
        raise NotImplementedError  # pragma: nocover

    def __enter__(self) -> Display:
        self.setup()
        if self._display is None:
            raise RuntimeError("Display is not initialised.")
        return self._display

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        self.cleanup()

        if self._display is not None:
            raise RuntimeError("The display was not cleaned up.")
