"""Driver for Waveshare 2in13bc display."""
import logging
import time
from math import ceil
from typing import Optional, List

import RPi.GPIO
import spidev
from PIL import Image

from einkd.display import Display

from .base import BaseDriver

CMD_PANEL_SETTING = 0x00
CMD_POWER_OFF = 0x02
CMD_POWER_ON = 0x04
CMD_BOOSTER_SOFT_START = 0x06
CMD_DEEP_SLEEP = 0x07
CMD_DATA_START_TRANSMISSION = 0x10
CMD_REFRESH = 0x12
CMD_DATA_START_TRANSMISSION2 = 0x13
CMD_VCOM_AND_DATA_INTERVAL_SETTING = 0x50
CMD_RESOLUTION_SETTING = 0x61

DATA_BOOSTER_SOFT_START = 0x17  # Always 0x17 from datasheet
DATA_DEEP_SLEEP_CHECK_CODE = 0xA5  # From datasheet

LOGGER = logging.getLogger(__name__)


class EPD2in13bcDisplay(Display):
    """An initialised e-ink display that we can control."""

    resolution = (212, 104)
    channels = ["black", "red"]

    def __init__(
        self,
        spi: spidev.SpiDev,
        reset_pin: int,
        dc_pin: int,
        cs_pin: int,
        busy_pin: int,
    ) -> None:
        self._spi = spi
        self._reset_pin = reset_pin
        self._dc_pin = dc_pin
        self._cs_pin = cs_pin
        self._busy_pin = busy_pin

        self.reset()
        self._init()

        self._buffers = {
            channel: [0xFF] * self.buffer_length
            for channel in self.channels
        }

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
        self._send_data(self.height & 0xff)
        self._send_data(self.width >> 8)  # 2^3 = 8
        self._send_data(self.width & 0xff)

    def _send_command(self, command: int) -> None:
        """
        Send an SPI command to the display.

        The commands are defined in the command table in the datasheet.

        :param command: The command to send.
        """
        LOGGER.debug(f"Sending command: {command}")
        RPi.GPIO.output(self._dc_pin, 0)  # Set to command mode.
        RPi.GPIO.output(self._cs_pin, 0)  # Select the e-ink screen.
        self._spi.writebytes([command])  # Send the command.
        RPi.GPIO.output(self._cs_pin, 1)  # De-select the e-ink screen.

    def _send_data(self, data: int, *, quiet: bool = False) -> None:
        """
        Send SPI data to the display.

        :param data: The data to send.
        """
        if not quiet:
            LOGGER.debug(f"Sending data {data}")
        RPi.GPIO.output(self._dc_pin, 1)  # Set to data mode.
        RPi.GPIO.output(self._cs_pin, 0)  # Select the e-ink screen.
        self._spi.writebytes([data])  # Send the data.
        RPi.GPIO.output(self._cs_pin, 1)  # De-select the e-ink screen.

    def _wait_busy(self) -> None:
        """
        Wait whilst the display is busy.

        The busy pin is high whilst the display is busy, so this function
        simply waits for the pin to go low.
        """
        LOGGER.debug("Waiting for display.")
        while RPi.GPIO.input(self._busy_pin) == 0:
            self._delay_ms(100)
        LOGGER.debug("Finished waiting for display")

    def _delay_ms(self, amount_ms: int) -> None:
        """
        Delay the program for some milliseconds.

        :param amount_ms: Number of milliseconds to delay for.
        """
        time.sleep(amount_ms / 1000.0)

    @property
    def buffer_length(self) -> int:
        """
        The length of the buffer for a single channel.

        :returns: The length of the buffer in bytes.
        """
        return ceil(self.width * self.height / 8)

    def reset(self) -> None:
        """
        Reset the display.

        Performs a hardware reset of the display.
        """
        LOGGER.debug("Display hardware reset")
        RPi.GPIO.output(self._reset_pin, 1)
        self._delay_ms(200)
        RPi.GPIO.output(self._reset_pin, 0)
        self._delay_ms(5)
        RPi.GPIO.output(self._reset_pin, 1)
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

    def _get_buffer(self, image: Image.Image) -> List[int]:
        """
        Calculate the bytes to send to a display for a given image.

        :param image: The image to display.
        :returns: The list of bytes to send.
        :raises ValueError: The image did not match the display size.
        """
        LOGGER.debug("Calculating pixel buffer")
        # Check that the image sizes match
        if image.size != self.resolution:
            raise ValueError(f"Image did not match display size: {image.size}")

        # Fill the buffer with all 1s
        buffer = [0xff] * self.buffer_length
        monocolour_image = image.convert("1")

        # Iterate through every pixel in the image.
        for y in range(self.height):
            for x in range(self.width):
                if monocolour_image.getpixel((x, self.height - y - 1)) == 0:
                    # If the pixel is a 0, flip the bit
                    byte_pos = (y + x * self.height) // 8
                    buffer[byte_pos] &= ~(0x80 >> (y % 8))

        return buffer

    def show(
        self,
        buffer: Image.Image,
        *,
        channel: Optional[str] = "black",
    ) -> None:
        """
        Set the image.

        :param buffer: The image to display on the channel.
        :param channel: The channel to set the data for, default to first.
        """
        if channel not in self.channels:
            raise ValueError(
                "Unknown channel: {channel}, expected one of {self.channels}.",
            )

        data = self._get_buffer(buffer)

        # Start the transmission
        if channel == "black":
            LOGGER.debug("Starting transmission of black channel data")
            self._send_command(CMD_DATA_START_TRANSMISSION)
        elif channel == "red":
            LOGGER.debug("Starting transmission of red channel data")
            self._send_command(CMD_DATA_START_TRANSMISSION2)
        else:
            # This code shouldn't be reachable.
            raise RuntimeError("Unknown channel: {channel}")

        # Send the pixel data
        LOGGER.debug("Sending pixel data")
        for pixel_byte in data:
            self._send_data(pixel_byte, quiet=True)

    def refresh(self) -> None:
        """
        Refresh the display.

        Refreshing the display should update the display to match the buffers.

        This function is blocking, and will wait until the display has refreshed.
        """
        LOGGER.debug("Refreshing display.")
        self._send_command(CMD_REFRESH)
        self._wait_busy()


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

        self._spi = spidev.SpiDev()

    def setup(self) -> None:
        """
        Set up the display.

        After this method has been run, _display should exist.

        This should fail if the display has already been setup.
        """
        LOGGER.debug("Display setup")
        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setup(self._reset_pin, RPi.GPIO.OUT)
        RPi.GPIO.setup(self._dc_pin, RPi.GPIO.OUT)
        RPi.GPIO.setup(self._cs_pin, RPi.GPIO.OUT)
        RPi.GPIO.setup(self._busy_pin, RPi.GPIO.IN)

        LOGGER.debug("Opening SPI")
        self._spi.open(self._spi_bus, self._spi_dev)
        self._spi.max_speed_hz = self._spi_max_speed
        self._spi.mode = 0b00
        self._display = EPD2in13bcDisplay(
            self._spi,
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

        RPi.GPIO.output(self._reset_pin, 0)
        RPi.GPIO.output(self._dc_pin, 0)

        RPi.GPIO.cleanup([
            self._reset_pin,
            self._dc_pin,
            self._cs_pin,
            self._busy_pin,
        ])

        self._display = None
