# einkd

A daemon and library for displaying images on e-ink displays.

## Supported Displays

| Manufacturer | Model       | Colours     | Resolution | Support   |
|--------------|-------------|-------------|------------|-----------|
| Waveshare    | 2.13" (B)   | Red & Black | 212 x 104  | Supported |
| Waveshare    | 7.5" HD (B) | Red & Black | 880 x 528  | Planned   |
| Waveshare    | 7.5" HD     | Black       | 880 x 528  | Planned   |

Displays usually require an SPI interface, for which the `spidev` module is used
to control them using the standard kernel interfaces.

Additionally, some displays may require additional GPIO pins to control them.