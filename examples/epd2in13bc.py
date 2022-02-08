"""Example code for the epd2in13bc driver."""

import logging

from time import sleep
from PIL import Image

from einkd.drivers.epd2in13bc import EPD2in13bcDriver

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with EPD2in13bcDriver() as epd:
        epd.clear()

        sleep(5)

        img = Image.open("examples/img/212x104-b.png")
        epd.show(img)
        epd.refresh()

        sleep(5)

        img = Image.open("examples/img/212x104-w.png")
        epd.show(img)
        epd.refresh()

        sleep(5)

        epd.clear()
