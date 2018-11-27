"""Develop and Test TLC5957."""

__doc__ = """
Develop and Test TLC5957.

this script contains a bunch of tests and debug outputs.
its mainly the playground during the development of the library.
"""

import time

import board
# import busio
import bitbangio
import pulseio
import digitalio

import slight_tlc5957

##########################################
print(
    "\n" +
    (42 * '*') + "\n" +
    __doc__ + "\n" +
    (42 * '*') + "\n" +
    "\n"
)

##########################################
print(42 * '*')
print("initialise digitalio pins for SPI")
spi_clock = digitalio.DigitalInOut(board.SCK)
spi_clock.direction = digitalio.Direction.OUTPUT
spi_mosi = digitalio.DigitalInOut(board.MOSI)
spi_mosi.direction = digitalio.Direction.OUTPUT
spi_miso = digitalio.DigitalInOut(board.MISO)
spi_miso.direction = digitalio.Direction.INPUT

# print((42 * '*') + "\n" + "init busio.SPI")
# spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
print("init bitbangio.SPI")
spi = bitbangio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# maximum frequency is currently hardcoded to 6MHz
# https://github.com/adafruit/circuitpython/blob/master/ports/atmel-samd/common-hal/pulseio/PWMOut.c#L119
gsclk_freqency = (6000 * 1000)  # 6MHz
# gsclk_freqency = (2 * 1000)  # 2kHz
gsclk = pulseio.PWMOut(
    board.D9, duty_cycle=(2 ** 15), frequency=gsclk_freqency)
print("gsclk.frequency: {:}MHz".format(gsclk.frequency / (1000*1000)))

latch = digitalio.DigitalInOut(board.D7)
latch.direction = digitalio.Direction.OUTPUT

##########################################
print(42 * '*')
print("define pixel array / init TLC5957")
num_leds = 16
pixels = slight_tlc5957.TLC5957(
    spi=spi,
    latch=latch,
    gsclk=gsclk,
    spi_clock=spi_clock,
    spi_mosi=spi_mosi,
    spi_miso=spi_miso,
    pixel_count=num_leds)

print("pixel_count", pixels.pixel_count)
print("chip_count", pixels.chip_count)

##########################################
print(42 * '*')
print("set colors")
for index in range(num_leds):
    # pixels[index] = (0.1, 0.1, 0.1)
    # float 0.00002 → int 00001
    pixels[index] = (0.0, 0.0, 0.00002)
    # pixels[index] = (1, 1, 1)
# pixels[0] = (1, 0, 0)
# pixels[1] = (0, 0.1, 0)
# pixels[2] = (0, 0, 1)
# pixels[3] = (1, 1, 1)

# pixels[0] = (65535, 0, 0)
pixels[0] = (100, 0, 0)

pixels[1] = (0, 1, 0)

# pixels[2] = (0, 0, 65535)
pixels[2] = (0, 0, 100)

pixels[3] = (10, 10, 10)
# pixels[3] = (65535, 65535, 65535)

print("pixels._buffer", pixels._buffer)


##########################################
print(42 * '*')
print("time meassurement:")
loop_count = 100
duration = 0
start_time = time.monotonic()
for index in range(loop_count):
    pixels.show()
end_time = time.monotonic()
duration = end_time - start_time
print(
    "'pixels.show()'"
    "duration: {}s for {} loops.\n"
    "\t{:.2f}ms per loop"
    "".format(
        duration,
        loop_count,
        (duration/loop_count)*1000
    )
)

duration = 0
for index in range(loop_count):
    start_time = time.monotonic()
    pixels.show()
    end_time = time.monotonic()
    duration += end_time - start_time
print(
    "'pixels.show()'"
    "duration: {}s for {} loops.\n"
    "\t{:.2f}ms per loop"
    "".format(
        duration,
        loop_count,
        (duration/loop_count)*1000
    )
)
##########################################
print(42 * '*')
print("loop..")
# while True:
#     pass
# color = (0.0, 0.0, 0.00002)
color = (0, 0, 1)
last_time = time.monotonic()
loop_count = 0
while True:
    loop_count += 1
    color = (0, 0, color[2] + 500)
    if color[2] > 65000:
        duration = time.monotonic() - last_time
        print(
            "duration: {}s for {} loops.\n"
            "\t{:.2f}ms per loop"
            "".format(
                duration,
                loop_count,
                (duration/loop_count)*1000
            )
        )
        # reset
        color = (0, 0, 0)
        last_time = time.monotonic()
        loop_count = 0
    for index in range(num_leds):
        pixels[index] = color
    # write data to chips
    pixels.show()
#     # wait a second
#     time.sleep(0.01)
