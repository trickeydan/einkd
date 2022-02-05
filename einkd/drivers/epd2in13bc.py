"""Driver for Waveshare 2in13bc display."""
from typing import Optional

from PIL import Image

from einkd.display import Display, DisplayChannel

from .base import BaseDriver


class EPD2in13bcDisplay(Display):
    """An initialised e-ink display that we can control."""

    resolution = (212, 104)
    channels = [
        DisplayChannel("black"),
        DisplayChannel("red"),
    ]

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
        print("buffer")

    def refresh(self) -> None:
        """
        Refresh the display.

        Refreshing the display should update the display to match the buffers.

        This function is blocking, and will wait until the display has refreshed.
        """
        print("Refresh")


class EPD2in13bcDriver(BaseDriver):
    """Driver for Waveshare 2.13" (B)."""

    def setup(self) -> None:
        """
        Set up the display.

        After this method has been run, _display should exist.

        This should fail if the display has already been setup.
        """
        self._display = EPD2in13bcDisplay()

    def cleanup(self) -> None:
        """
        Clean up the display.

        After this method has been run, _display should be None.
        """
        self._display = None
