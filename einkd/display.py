"""Base classes for controlling an e-ink display."""

import logging
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from PIL import Image

LOGGER = logging.getLogger(__name__)


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
    def channels(self) -> List[str]:
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
        channel: Optional[str] = None,
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

    @property
    def width(self) -> int:
        """
        Get the width of the display.

        :returns: The width of the display, in pixels.
        """
        width, _ = self.resolution
        return width

    @property
    def height(self) -> int:
        """
        Get the height of the display.

        :returns: The height of the display, in pixels.
        """
        _, height = self.resolution
        return height

    def clear(self, *, refresh: bool = True) -> None:
        """
        Clear the display.

        :param refresh: Refresh the display.
        """
        LOGGER.debug("Clearing display")
        img = Image.new("1", self.resolution, 255)
        for channel in self.channels:
            self.show(img, channel=channel)

        if refresh:
            self.refresh()
