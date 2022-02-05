"""Base classes for controlling an e-ink display."""

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from PIL import Image


class DisplayChannel:
    """
    A channel on the display.

    Each channel represents an individual colour, other than white.
    """

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """
        The name of the display.

        :returns: The name of the display.
        """
        return self._name


class Display(metaclass=ABCMeta):
    """An initialised e-ink display that we can control."""

    @property
    @abstractmethod
    def resolution(self) -> Tuple[int, int]:
        """
        The resolution of the display.

        :returns: The resolution of the display.
        """
        raise NotImplementedError  # pragma: nocover

    @property
    @abstractmethod
    def channels(self) -> List[DisplayChannel]:
        """
        The channels available on this display.

        :returns: The list of available channels.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def show(
        self,
        buffer: Image.Image,
        *,
        channel: Optional[DisplayChannel] = None,
    ) -> None:
        """
        Set the image.

        :param buffer: The image to display on the channel.
        :param channel: The channel to set the data for, default to first.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def refresh(self) -> None:
        """
        Refresh the display.

        Refreshing the display should update the display to match the buffers.

        This function is blocking, and will wait until the display has refreshed.
        """
        raise NotImplementedError  # pragma: nocover

    def clear(self, *, refresh: bool = True) -> None:
        """
        Clear the display.

        :param refresh: Refresh the display.
        """
        img = Image.new("1", self.resolution)
        for channel in self.channels:
            self.show(img, channel=channel)

        if refresh:
            self.refresh()
