"""Virtual display."""
import tkinter
from typing import Optional, Tuple

from PIL import Image
from PIL.ImageTk import PhotoImage

from einkd.display import Display

from .base import BaseDriver


class TkinterDisplay(Display):
    """An initialised e-ink display that we can control."""

    colour_mode = "RGB"

    channels = ["black"]

    def __init__(self, resolution: Tuple[int, int]) -> None:
        self._resolution = resolution

        self.window = tkinter.Tk()
        self.window.wm_title("einkd")
        self.window.resizable(False, False)
        self.window.geometry(f"{self.width}x{self.height}")
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()
        self.label = tkinter.Label(self.frame)
        self.label.pack()

    @property
    def resolution(self) -> Tuple[int, int]:
        """
        The resolution of the display.

        :returns: The resolution of the display.
        """
        return self._resolution

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
        tkinter_image = PhotoImage(buffer)
        self.label.imagetk = tkinter_image  # type: ignore
        self.label.configure(image=tkinter_image)

    def refresh(self) -> None:
        """
        Refresh the display.

        Refreshing the display should update the display to match the buffers.

        This function is blocking, and will wait until the display has refreshed.
        """
        self.window.update_idletasks()
        self.window.update()


class TkinterDriver(BaseDriver):
    """Driver for Tkinter display."""

    _display: Optional[TkinterDisplay] = None

    def __init__(self, resolution: Tuple[int, int]) -> None:
        self._resolution = resolution

    def setup(self) -> None:
        """
        Set up the display.

        After this method has been run, _display should exist.

        This should fail if the display has already been setup.
        """
        self._display = TkinterDisplay(self._resolution)

    def cleanup(self) -> None:
        """
        Clean up the display.

        After this method has been run, _display should be None.
        """
        if self._display is not None:
            self._display.window.quit()
            self._display = None
