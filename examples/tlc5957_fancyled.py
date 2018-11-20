"""Simple & Minimallistic example for the TLC5957 library."""

import board
import busio
import pulseio
import digitalio

import slight_tlc5957
import adafruit_fancyled.adafruit_fancyled as fancyled

spi = busio.SPI(board.SCK, MOSI=board.MOSI)

gsclk = pulseio.PWMOut(
    board.D9, duty_cycle=(2 ** 15), frequency=(10 * 1000))

latch = digitalio.DigitalInOut(board.D7)
latch.direction = digitalio.Direction.OUTPUT

# define pixel array
num_leds = 16
pixels = slight_tlc5957.TLC5975(
    spi, latch, gsclk, num_leds)


# set first pixel to orange
# using floating point values (0..1)
pixels[0] = (1, 0.5, 0)
# set first pixel to sky blue
# using 16bit integer values (0..65535)
pixels[1] = (0, 32000, 65535)


# Declare a 6-element RGB rainbow palette
palette = [
    fancyled.CRGB(1.0, 0.0, 0.0),  # Red
    fancyled.CRGB(0.5, 0.5, 0.0),  # Yellow
    fancyled.CRGB(0.0, 1.0, 0.0),  # Green
    fancyled.CRGB(0.0, 0.5, 0.5),  # Cyan
    fancyled.CRGB(0.0, 0.0, 1.0),  # Blue
    fancyled.CRGB(0.5, 0.0, 0.5),  # Magenta
]

# Positional offset into color palette to get it to 'spin'
offset = 0

##########################################
# main loop
while True:
    for i in range(num_leds):
        # Load each pixel's color from the palette using an offset, run it
        # through the gamma function, pack RGB value and assign to pixel.
        color = fancyled.palette_lookup(palette, offset + i / num_leds)
        # color = fancyled.gamma_adjust(color, brightness=0.25)
        pixels[i] = color
    pixels.show()

    offset += 0.001  # Bigger number = faster spin
