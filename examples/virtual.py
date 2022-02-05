"""Example code for the epd2in13bc driver."""
from time import sleep

from PIL import Image

from einkd.drivers.virtual import TkinterDriver

images = [
    'examples/img/880x528-b.png',
    'examples/img/880x528-w.png',
    'examples/img/880x528-r.png',
]

if __name__ == "__main__":

    with TkinterDriver((800, 528)) as epd:
        epd.clear()

        for img_name in images:
            img = Image.open(img_name)
            epd.show(img)
            epd.refresh()
            sleep(5)
