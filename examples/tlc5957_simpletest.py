"""Simple & Minimallistic example for the TLC5957 library."""

import board
import busio
import pulseio
import digitalio

import slight_tlc5957

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

# write data to chips
pixels.show()
