"""Example code for the epd2in13bc driver."""

import logging

from einkd.drivers.epd2in13bc import EPD2in13bcDriver

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with EPD2in13bcDriver() as epd:
        epd.clear()
