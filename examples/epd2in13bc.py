"""Example code for the epd2in13bc driver."""

from einkd.drivers.epd2in13bc import EPD2in13bcDriver

if __name__ == "__main__":

    with EPD2in13bcDriver() as epd:
        epd.clear()
