import tkinter

from PIL import Image
from PIL.ImageTk import PhotoImage

from .display import Display


class EInkDisplay(Display):

    colour_mode = "L"

    def __init__(
        self,
        width: int,
        height: int,
        *,
        title: str = "LibreFrame",
    ) -> None:
        self.width = width
        self.height = height

        self.window = tkinter.Tk()
        self.window.wm_title(title)
        self.window.resizable(False, False)
        self.window.geometry(f"{width}x{height}")
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()
        self.label = tkinter.Label(self.frame)
        self.label.pack()

    def draw(self, image: Image) -> None:
        tkinter_image = PhotoImage(image)
        self.label.imagetk = tkinter_image  # type: ignore
        self.label.configure(image=tkinter_image)
        self.window.update_idletasks()
        self.window.update()

    def start(self) -> None:
        self.window.update_idletasks()
        self.window.update()

    def stop(self) -> None:
        self.window.quit()