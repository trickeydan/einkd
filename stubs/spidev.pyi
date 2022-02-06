"""Partial stubs for spidev."""
from typing import List

class SpiDev:

    max_speed_hz: int
    mode: int

    def close(self) -> None: ...
    def open(self, bus: int, device: int) -> None: ...
    def writebytes(self, data: List[int]) -> None: ...
