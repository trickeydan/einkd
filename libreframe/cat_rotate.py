from libreframe.api.client import APIClient
from pathlib import Path
from time import sleep

from libreframe.gui import Window
from libreframe.gui.components import ImageComponent, TextComponent

from libreframe.display import EInkDisplay


image = ImageComponent("image", file_path=Path("/home/dan/openreachboji.png"),cell_y=11)
text = TextComponent("title", cell_y=1, text="bees")

w = Window(880, 528, components={(0,0): image, (0, 11): text})

api = APIClient("https://api.trickey.io/frame", "cat")

with EInkDisplay(880, 528) as d:
    for res in api:
        image.file_path = Path(res.file)
        text._text = res.photo.description
        d.display(w)
        sleep(api.photo_time)
