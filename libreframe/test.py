from pathlib import Path
from time import sleep

from libreframe.gui import Window
from libreframe.gui.components import FilledComponent, ImageComponent

from libreframe.display import EInkDisplay

w = Window(880, 528, components={(0,0): FilledComponent("black", 12, 1, colour="#000000")})

with EInkDisplay(880, 528) as d:
    for _ in range (5):
        w.components = {
            (0,0): FilledComponent("black", 12, 1, colour="#000000"),
            (0,1): ImageComponent("im", 4, 11, file_path=Path("/home/dan/Documents/DanTrickeyIDCard.jpg")),
            # (4,1): ImageComponent("im2", 8, 11, file_path=Path("/home/dan/openreachboji.png")),
        }
        d.display(w)
        sleep(1)
        w.components = {
            (0,0): FilledComponent("black", 12, 1, colour="#000000"),
            (0,1): FilledComponent("not_black", 12, 2, colour="#ff00ff"),
            (0,3): FilledComponent("not_black2", 3, 9, colour="#ffffff"),
            (3,3): FilledComponent("not_black3", 3, 9, colour="#3dcaad"),
            # (6,3): ImageComponent("not_black4", 3, 9, file_path=Path("/home/dan/openreachboji.png")),
            (9,3): FilledComponent("not_black5", 3, 9, colour="#3dcaad"),
        }
        d.display(w)
        sleep(1)
        # w.components[(6,3)].file_path = Path("/home/dan/Documents/DanTrickeyIDCard.jpg")
        d.display(w)
        sleep(1)
