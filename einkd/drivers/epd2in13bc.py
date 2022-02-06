"""Driver for Waveshare 2in13bc display."""
import logging
import time
from typing import Optional

import RPi.GPIO
import spidev
from PIL import Image

from einkd.display import Display, DisplayChannel

from .base import BaseDriver

CMD_PANEL_SETTING = 0x00
CMD_POWER_OFF = 0x02
CMD_POWER_ON = 0x04
CMD_BOOSTER_SOFT_START = 0x06
CMD_DEEP_SLEEP = 0x07
CMD_VCOM_AND_DATA_INTERVAL_SETTING = 0x50
CMD_RESOLUTION_SETTING = 0x61

DATA_BOOSTER_SOFT_START = 0x17  # Always 0x17 from datasheet
DATA_DEEP_SLEEP_CHECK_CODE = 0xA5  # From datasheet

LOGGER = logging.getLogger(__name__)


class EPD2in13bcDisplay(Display):
    """An initialised e-ink display that we can control."""

    resolution = (212, 104)
    channels = [
        DisplayChannel("black"),
        DisplayChannel("red"),
    ]

    def __init__(
        self,
        spi: spidev.SpiDev,
        gpio: RPi.GPIO,
        reset_pin: int,
        dc_pin: int,
        cs_pin: int,
        busy_pin: int,
    ) -> None:
        self._spi = spi
        self._gpio = gpio
        self._reset_pin = reset_pin
        self._dc_pin = dc_pin
        self._cs_pin = cs_pin
        self._busy_pin = busy_pin

        self.reset()
        self._init()

    def _init(self) -> None:
        """Initialise the display."""
        LOGGER.debug("Initialising")
        # Perform a booster soft start.
        self._send_command(CMD_BOOSTER_SOFT_START)
        self._send_data(DATA_BOOSTER_SOFT_START)
        self._send_data(DATA_BOOSTER_SOFT_START)
        self._send_data(DATA_BOOSTER_SOFT_START)

        # This command will turn on booster, controller, regulators, and temperature
        # sensor will be activated for one-time sensing before enabling booster.
        # When all voltages are ready, the BUSY_N signal will return to high.
        self._send_command(CMD_POWER_ON)
        self._wait_busy()

        # Configure the panel with settings
        # 0x8F = 1000 1111
        # RES[1:0] = 10b - Set Display Resolution to 128x196
        # REG_EN   = 0b  - LUT from OTP
        # BWR      = 0   - Pixel with B / W / Red
        # UD       = 1   - Gate Scan direction is up
        # SHL      = 1   - Source Shift direction is right
        # SHD_N    = 1   - Set booster switch to on.
        # RST_N    = 1   - No effect, soft reset is only option.
        self._send_command(CMD_PANEL_SETTING)
        self._send_data(0x8f)

        # This command indicates the interval of VCOM and data output. When setting the
        # vertical back porch, the total blanking will be kept (20 Hsync).
        # 0xF0 = 1111 0000
        # VBD[1:0] = 11b   - LUTB
        # DDX[1:0] = 11b   - LUTW
        # CDI[3:0] = 0000b - 17 hsync
        self._send_command(CMD_VCOM_AND_DATA_INTERVAL_SETTING)
        self._send_data(0xf0)

        # This command defines alternative display resoltuon and is of higher priority
        # than the resolution selected in CMD_POWER_ON
        self._send_command(CMD_RESOLUTION_SETTING)
        self._send_data(self.width & 0xff)
        self._send_data(self.height >> 8)  # 2^3 = 8
        self._send_data(self.height & 0xff)

    def _send_command(self, command: int) -> None:
        """
        Send an SPI command to the display.

        The commands are defined in the command table in the datasheet.

        :param command: The command to send.
        """
        LOGGER.debug(f"Sending command: {command}")
        self._gpio.output(self._dc_pin, 0)  # Set to command mode.
        self._gpio.output(self._cs_pin, 0)  # Select the e-ink screen.
        self._spi.writebytes([command])  # Send the command.
        self._gpio.output(self._cs_pin, 1)  # De-select the e-ink screen.

    def _send_data(self, data: int) -> None:
        """
        Send SPI data to the display.

        :param data: The data to send.
        """
        LOGGER.debug(f"Sending data {data}")
        self._gpio.output(self._dc_pin, 1)  # Set to data mode.
        self._gpio.output(self._cs_pin, 0)  # Select the e-ink screen.
        self._spi.writebytes([data])  # Send the data.
        self._gpio.output(self._cs_pin, 1)  # De-select the e-ink screen.

    def _wait_busy(self) -> None:
        """
        Wait whilst the display is busy.

        The busy pin is high whilst the display is busy, so this function
        simply waits for the pin to go low.
        """
        LOGGER.debug("Waiting for display.")
        while self._gpio.input(self._busy_pin) == 0:
            self._delay_ms(100)
        LOGGER.debug("Display is done.")

    def _delay_ms(self, amount_ms: int) -> None:
        """
        Delay the program for some milliseconds.

        :param amount_ms: Number of milliseconds to delay for.
        """
        LOGGER.debug(f"Waiting {amount_ms}ms")
        time.sleep(amount_ms / 1000.0)

    def reset(self) -> None:
        """
        Reset the display.

        Performs a hardware reset of the display.
        """
        LOGGER.debug("Display hardware reset")
        self._gpio.output(self._reset_pin, 1)
        self._delay_ms(200)
        self._gpio.output(self._reset_pin, 0)
        self._delay_ms(5)
        self._gpio.output(self._reset_pin, 1)
        self._delay_ms(200)

    def sleep(self) -> None:
        """
        Put the display into deep sleep.

        After this function has been called, the display will become unresponsive
        until it has been reset.
        """
        LOGGER.debug("Setting display to sleep")
        # After the Power OFF command, the driver will be powered OFF. Refer to the
        # POWER MANAGEMENT section for the sequence. This command will turn off booster,
        # controller, source driver, gate driver, VCOM, and temperature sensor, but
        # register data will be kept until VDD turned OFF or Deep Sleep Mode.
        self._send_command(CMD_POWER_OFF)
        self._wait_busy()

        # After this command is transmitted, the chip will enter Deep Sleep Mode
        # to save power. Deep Sleep Mode will return to Standby Mode by hardware reset.
        # The only one parameter is a check code, the command will be executed
        # if and only if check code = 0xA5.
        self._send_command(CMD_DEEP_SLEEP)
        self._send_data(DATA_DEEP_SLEEP_CHECK_CODE)

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

    def __init__(
        self,
        *,
        reset_pin: int = 17,
        dc_pin: int = 25,
        cs_pin: int = 8,
        busy_pin: int = 24,
        spi_bus: int = 0,
        spi_dev: int = 0,
        spi_max_speed: int = 4000000,
    ) -> None:
        self._reset_pin = reset_pin
        self._dc_pin = dc_pin
        self._cs_pin = cs_pin
        self._busy_pin = busy_pin
        self._spi_bus = spi_bus
        self._spi_dev = spi_dev
        self._spi_max_speed = spi_max_speed

        self._spi = spidev.spidev.SpiDev()
        self._gpio = RPi.GPIO

    def setup(self) -> None:
        """
        Set up the display.

        After this method has been run, _display should exist.

        This should fail if the display has already been setup.
        """
        LOGGER.debug("Display setup")
        self._gpio.setmode(self._gpio.BCM)
        self._gpio.setwarnings(False)
        self._gpio.setup(self._reset_pin, self._gpio.OUT)
        self._gpio.setup(self._dc_pin, self._gpio.OUT)
        self._gpio.setup(self._cs_pin, self._gpio.OUT)
        self._gpio.setup(self._busy_pin, self._gpio.IN)

        LOGGER.debug("Opening SPI")
        self._spi.open(self._spi_bus, self._spi_dev)
        self._spi.max_speed_hz = self._spi_max_speed
        self._spi.mode = 0b00
        self._display = EPD2in13bcDisplay(
            self._spi,
            self._gpio,
            self._reset_pin,
            self._dc_pin,
            self._cs_pin,
            self._busy_pin,
        )

    def cleanup(self) -> None:
        """
        Clean up the display.

        After this method has been run, _display should be None.
        """
        LOGGER.debug("Cleaning up display.")
        self._spi.close()

        self._gpio.output(self._reset_pin, 0)
        self._gpio.output(self._dc_pin, 0)

        self._gpio.cleanup([
            self._reset_pin,
            self._dc_pin,
            self._cs_pin,
            self._busy_pin,
        ])

        self._display = None
