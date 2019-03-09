#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CircuitPython

"""Power Test TLC5957."""

__doc__ = """
Power Test your TLC5957 Board.

test your TLC5957 based Board for power consumption.
"""

import time

import board
# import busio
import bitbangio
import digitalio
import pulseio
import supervisor

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
    board.D9,
    duty_cycle=(2 ** 15),
    frequency=gsclk_freqency,
    variable_frequency=True)
print("gsclk.frequency: {:}MHz".format(gsclk.frequency / (1000*1000)))

latch = digitalio.DigitalInOut(board.D7)
latch.direction = digitalio.Direction.OUTPUT

##########################################
print(42 * '*')
print("define pixel array / init TLC5957")
num_leds = 16*2
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
# for index in range(4):
#     # pixels[index] = (0.0, 0.0, 0.00002)
#     pixels[index] = (1, 1, 1)
pixels.set_pixel_all((0.01, 0.1, 0.01))
# for i in range(num_leds):
#     # pixels[i] = (0.1, 0.1, 0.1)
#     pixels.set_pixel(i, (0.1, 0.1, 0.1))
pixels.show()
time.sleep(1)
pixels.set_pixel_all((0.1, 0.1, 0.1))
pixels.show()


##########################################
print(42 * '*')
print("fc things")
pixels.print_buffer_fc()

# for i in range(pixels.chip_count):
#     pixels.set_fc_bits_in_buffer(
#         chip_index=i,
#         field=slight_tlc5957.TLC5957._FC_FIELDS["CCR"],
#         value=value_CC
#     )
# value_CC = 0x000
# value_CC = 0x001
# value_CC = 0x010
# value_CC = 0x100
# value_CC = 0x150
value_CC = 0x1FF
pixels.set_fc_CC_all(value_CC, value_CC, value_CC)
pixels.print_buffer_fc()
pixels.update_fc()
##########################################
print(42 * '*')
print("loop..")

if supervisor.runtime.serial_connected:
    print("you can change the brightness:")
    print("new brightness (0..1): ")
while True:
    if supervisor.runtime.serial_bytes_available:
        new_value = input()
        new_brightness = gsclk.frequency
        try:
            new_brightness = float(new_value)
        except ValueError as e:
            print("Exception: ", e)
        print(
            "calculated brightness: {:}".format(
                new_brightness
            )
        )
        pixels.set_pixel_all((new_brightness, new_brightness, new_brightness))
        pixels.show()
        # prepare new input
        print("\nenter new brightness (0..1): ")
