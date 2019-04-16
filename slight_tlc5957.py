#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CircuitPython

# The MIT License (MIT)
#
# Copyright (c) 2018 Stefan Krüger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# 1 blank line required between summary line and description
# pylama:ignore=D205

u"""
s-light CircuitPython TLC5957 library.
====================================================

CircuitPython library for
`TI TLC5957 48-channel 16bit LED-Driver
<http://www.ti.com/product/TLC5957/>`_

* Author(s): Stefan Krüger


Implementation Notes
--------------------

**Hardware:**

* example PCB with TLC5957 and 4x4 SMD RGB LEDs
  https://github.com/s-light/magic_amulet_pcbs/tree/master/LEDBoard_4x4_HD

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/s-light/slight_CircuitPython_TLC5957.git"

# imports

# import time

# from enum import Enum, unique
# https://docs.python.org/3/library/enum.html
# currently not supported by CircuitPython


class TLC5957(object):
    """TLC5957 16-bit 48 channel LED PWM driver.

    This chip is designed to drive 16 RGB LEDs with 16-bit PWM per Color.
    The class has an interface compatible with FancyLED.
    and with this is similar to the NeoPixel and DotStar Interfaces.

    :param ~busio.SPI spi: An instance of the SPI bus connected to the chip.
        The clock and MOSI must be set
        the MISO (input) is currently unused.
        Maximal data clock frequence is:
        - TLC5957: 33MHz
    :param ~digitalio.DigitalInOut latch: The chip LAT (latch) pin object
        that implements the DigitalInOut API.
    :param ~pulseio.PWMOut gsclk: The chip Grayscale Clock pin object
        that implements the PWMOut API.
    :param bool pixel_count: Number of RGB-LEDs (=Pixels) are connected.
    """

    # TLC5957 data / register structure
    #
    # some detailed information on the protocol based on
    # http://www.ti.com/lit/ds/symlink/t

    ##########################################
    # helper
    ##########################################

    COLORS_PER_PIXEL = 3
    PIXEL_PER_CHIP = 16
    CHANNEL_PER_CHIP = COLORS_PER_PIXEL * PIXEL_PER_CHIP

    BUFFER_BYTES_PER_COLOR = 2
    BUFFER_BYTES_PER_PIXEL = BUFFER_BYTES_PER_COLOR * COLORS_PER_PIXEL

    CHIP_BUFFER_BIT_COUNT = 48
    CHIP_BUFFER_BYTE_COUNT = CHIP_BUFFER_BIT_COUNT // 8
    CHIP_GS_BUFFER_BYTE_COUNT = CHIP_BUFFER_BYTE_COUNT * PIXEL_PER_CHIP
    CHIP_FUNCTION_CMD_BIT_COUNT = 16
    CHIP_FUNCTION_CMD_BYTE_COUNT = CHIP_FUNCTION_CMD_BIT_COUNT // 8

    @staticmethod
    def set_bit_with_mask(value, mask, value_new):
        """Set bit with help of mask."""
        # clear
        value &= ~mask
        if value_new:
            # set
            value |= mask
        return value

    @staticmethod
    def set_bit(value, index, value_new):
        """Set bit - return new value.

        Set the index:th bit of value to 1 if value_new is truthy,
        else to 0, and return the new value.
        https://stackoverflow.com/a/12174051/574981
        """
        # Compute mask, an integer with just bit 'index' set.
        mask = 1 << index
        # Clear the bit indicated by the mask (if x is False)
        value &= ~mask
        if value_new:
            # If x was True, set the bit indicated by the mask.
            value |= mask
        # Return the result, we're done.
        return value

    ##########################################
    # class Function_Command():
    # """
    # Enum for available function commands.
    #
    # 3.10 Function Commands Summary (page 30)
    # http:#www.ti.com/lit/ug/slvuaf0/slvuaf0.pdf#page=30&zoom=auto,-110,464
    #
    # WRTGS
    # -----
    #     48-bit GS data write
    #     copy common 48bit to GS-data-latch[GS-counter]
    #     GS-counter -1
    # LATGS
    # -----
    #     latch grayscale
    #     (768-bit GS data latch)
    #     copy common 48bit to GS-data-latch[0]
    #     if XREFRESH = 0
    #         GS-data-latch copy to GS-data-latch 2
    #     if XREFRESH = 1
    #         GS-data-latch copy to GS-data-latch 2
    # WRTFC
    # -----
    #     write FC data
    #     copy common 48bit to FC-data
    #     if used after FCWRTEN
    # LINERESET
    # ---------
    #     Line Counter register clear.
    #     copy common 48bit to GS-data-latch[0]
    #     data-latch-counter reset
    #     if XREFRESH = 0
    #         Autorefresh enabled
    #         wehn GS-counter == 65535: GS-data-latch copyto GS-data-latch2
    #     if XREFRESH = 1
    #         Autorefresh disabled
    #         GS-data-latch copy to GS-data-latch 2
    #         GS-counter reset
    #         OUTx forced off
    #     change group pattern when received
    # READFC
    # ------
    #     read FC data
    #     copy FC-data to common 48bit
    #     (can be read at SOUT)
    # TMGRST
    # ------
    #     reset line-counter
    #     GS-counter = 0
    #     OUTx forced off
    # FCWRTEN
    # -------
    #     enable writes to FC
    #     this must send before WRTFC
    # """

    _FC__WRTGS = 1
    _FC__LATGS = 3
    _FC__WRTFC = 5
    _FC__LINERESET = 7
    _FC__READFC = 11
    _FC__TMGRST = 13
    _FC__FCWRTEN = 15

    ##########################################
    # 3.3.3 Function Control (FC) Register
    # BIT     NAME            default     description
    # 0-1     LODVTH          01          LED Open Detection Voltage
    # 2-3     SEL_TD0         01          TD0 select. SOUT hold time.
    # 4       SEL_GDLY        1           Group Delay. 0 = No Delay
    # 5       XREFRESH        0           auto data refresh mode.
    #                                     on LATGS/LINERESET → data copied
    #                                       from GS1 to GS2
    #                                     0 = enabled → GS-counter continues
    #                                     1 = disabled → GS-counter reset;
    #                                       OUTx forced off
    # 6       SEL_GCK_EDGE    0           GCLK edge select.
    #                                     0 = OUTx toggle only on
    #                                       rising edge of GLCK
    #                                     1 = OUTx toggle on
    #                                       rising & falling edge of GLCK
    # 7       SEL_PCHG        0           Pre-charge working mode select
    # 8       ESPWM           0           ESPWM mode enable bit.
    #                                       (0 = enabled, 1 = disabled)
    # 9       LGSE3           0           Compensation for Blue LED.
    #                                       (0 = disabled, 1 = enabled)
    # 10      SEL_SCK_EDGE    0           SCLK edge select
    #                                       (0 = rising edge, 1 = both edges)
    # 11-13   LGSE1           000         Low Gray Scale Enhancement for
    #                                       Red/Green/Blue color
    # 14-22   CCB             100000000   Color brightness control data Blue
    #                                       (000h-1FFh)
    # 23-31   CCG             100000000   Color brightness control data Green
    #                                       (000h-1FFh)
    # 32-40   CCR             100000000   Color brightness control data Red
    #                                       (000h-1FFh)
    # 41-43   BC              100         Global brightness control data
    #                                       (0h-7h)
    # 44      PokerTransMode  0           Poker trans mode enable bit.
    #                                       (0 = disabled, 1 = enabled)
    # 45-47   LGSE2           000         first line performance improvment

    # _FC_CHIP_BUFFER_BIT_OFFSET = _BC_BIT_COUNT
    _FC_BIT_COUNT = CHIP_BUFFER_BIT_COUNT
    _FC_FIELDS = {
        "LODVTH": {
            "offset": 0,
            "length": 2,
            "mask": 0b11,
            "default": 0b01,
        },
        "SEL_TD0": {
            "offset": 2,
            "length": 2,
            "mask": 0b11,
            "default": 0b01,
        },
        "SEL_GDLY": {
            "offset": 4,
            "length": 1,
            "mask": 0b1,
            "default": 0b1,
        },
        "XREFRESH": {
            "offset": 5,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "SEL_GCK_EDGE": {
            "offset": 6,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "SEL_PCHG": {
            "offset": 7,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "ESPWM": {
            "offset": 8,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "LGSE3": {
            "offset": 9,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "LGSE1": {
            "offset": 11,
            "length": 3,
            "mask": 0b111,
            "default": 0b000,
        },
        "CCB": {
            "offset": 14,
            "length": 9,
            "mask": 0b111111111,
            "default": 0b100000000,
        },
        "CCG": {
            "offset": 23,
            "length": 9,
            "mask": 0b111111111,
            "default": 0b100000000,
        },
        "CCR": {
            "offset": 32,
            "length": 9,
            "mask": 0b111111111,
            "default": 0b100000000,
        },
        "BC": {
            "offset": 41,
            "length": 3,
            "mask": 0b111,
            "default": 0b100,
        },
        "PokerTransMode": {
            "offset": 44,
            "length": 1,
            "mask": 0b1,
            "default": 0b0,
        },
        "LGSE2": {
            "offset": 45,
            "length": 3,
            "mask": 0b111,
            "default": 0b000,
        },
    }

    ##########################################

    ##########################################

    def __init__(
            self,
            # *,    # this forces all following parameter to be named
            spi,
            spi_clock,
            spi_mosi,
            spi_miso,
            latch,
            gsclk,
            pixel_count=16):
        """Init."""
        # i don't see a better way to get all this initialised...
        # pylint: disable=too-many-arguments

        self._spi = spi
        self._spi_clock = spi_clock
        self._spi_mosi = spi_mosi
        self._spi_miso = spi_miso
        self._latch = latch
        self._gsclk = gsclk
        # how many pixels are there?
        self.pixel_count = pixel_count
        # print("pixel_count", self.pixel_count)
        # calculate how many chips are needed
        self.chip_count = self.pixel_count // self.PIXEL_PER_CHIP
        if self.pixel_count % self.PIXEL_PER_CHIP > 0:
            self.chip_count += 1
        # print("chip_count", self.chip_count)
        self.channel_count = self.pixel_count * self.COLORS_PER_PIXEL

        # data is stored in raw buffer
        self._buffer = bytearray(
            self.CHIP_GS_BUFFER_BYTE_COUNT * self.chip_count)
        # print("CHIP_GS_BUFFER_BYTE_COUNT", self.CHIP_GS_BUFFER_BYTE_COUNT)
        # print("_buffer", self._buffer)

        self._buffer_fc = bytearray(
            self.CHIP_BUFFER_BYTE_COUNT * self.chip_count)
        self._init_buffer_fc()
        self.update_fc()
        # self.print_buffer_fc()

        # write initial 0 values
        self.show()
        self.show()

    def _write_buffer_GS(self):
        # Write out the current state to the shift register.
        buffer_start = 0
        write_count = (
            (self.CHIP_BUFFER_BYTE_COUNT * self.chip_count)
            - self.CHIP_FUNCTION_CMD_BYTE_COUNT)

        for index in range(self.PIXEL_PER_CHIP):
            try:
                # wait untill we have access to / locked SPI bus
                while not self._spi.try_lock():
                    pass
                # configure
                # 10kHz
                # baudrate = (10 * 1000)
                # 1MHz
                # baudrate = (1000 * 1000)
                # 10MHz
                baudrate = (10 * 1000 * 1000)
                self._spi.configure(
                    baudrate=baudrate, polarity=0, phase=0, bits=8)

                # write data
                # self._spi.write(
                #     self._buffer, start=buffer_start, end=write_count)

                # workaround for bitbangio.SPI.write missing start & end
                buffer_in = bytearray(write_count)
                self._spi.write_readinto(
                    self._buffer,
                    buffer_in,
                    out_start=buffer_start,
                    out_end=buffer_start + write_count)

            finally:
                # Ensure the SPI bus is unlocked.
                self._spi.unlock()
            buffer_start += write_count
            # special
            if index == self.PIXEL_PER_CHIP - 1:
                self._write_buffer_with_function_command(
                    self._FC__LATGS, buffer_start, self._buffer)
            else:
                self._write_buffer_with_function_command(
                    self._FC__WRTGS, buffer_start, self._buffer)
            buffer_start += self.CHIP_FUNCTION_CMD_BYTE_COUNT

    def _write_buffer_FC(self):
        # Write out the current state to the shift register.
        buffer_start = 0
        write_count = (
            (self.CHIP_BUFFER_BYTE_COUNT * self.chip_count)
            - self.CHIP_FUNCTION_CMD_BYTE_COUNT)

        # enable FC write
        self._write_buffer_with_function_command(
            self._FC__FCWRTEN, buffer_start, self._buffer_fc)

        try:
            # wait untill we have access to / locked SPI bus
            while not self._spi.try_lock():
                pass
            # configure
            # 10kHz
            # baudrate = (10 * 1000)
            # 1MHz
            # baudrate = (1000 * 1000)
            # 10MHz
            baudrate = (10 * 1000 * 1000)
            self._spi.configure(
                baudrate=baudrate, polarity=0, phase=0, bits=8)

            # write data
            # self._spi.write(
            #     self._buffer, start=buffer_start, end=write_count)

            # workaround for bitbangio.SPI.write missing start & end
            buffer_in = bytearray(write_count)
            self._spi.write_readinto(
                self._buffer_fc,
                buffer_in,
                out_start=buffer_start,
                out_end=buffer_start + write_count)

        finally:
            # Ensure the SPI bus is unlocked.
            self._spi.unlock()
        buffer_start += write_count
        # special
        self._write_buffer_with_function_command(
            self._FC__WRTFC, buffer_start, self._buffer_fc)
        # done.

    def _write_buffer_with_function_command(
            self,
            function_command,
            buffer_start,
            buffer):
        """Bit-Banging SPI write to sync with latch pulse."""
        # combine two 8bit buffer parts to 16bit value
        value = (
            (buffer[buffer_start + 0] << 8) |
            buffer[buffer_start + 1]
        )

        self._spi_clock.value = 0
        self._spi_mosi.value = 0
        self._latch.value = 0
        latch_start_index = self.CHIP_FUNCTION_CMD_BIT_COUNT - function_command
        for index in range(self.CHIP_FUNCTION_CMD_BIT_COUNT):
            if latch_start_index == index:
                self._latch.value = 1

            # b1000000000000000
            if value & 0x8000:
                self._spi_mosi.value = 1
            else:
                self._spi_mosi.value = 0
            value <<= 1

            # CircuitPython needs 14us for this setting pin high and low again.
            self._spi_clock.value = 1
            # 1ms
            # time.sleep(0.001)
            # 100us
            # time.sleep(0.0001)
            # 10us
            # time.sleep(0.00001)
            self._spi_clock.value = 0

        self._latch.value = 0

    def show(self):
        """Write out Grayscale Values to chips."""
        self._write_buffer_GS()

    def update_fc(self):
        """Write out Function_Command Values to chips."""
        self._write_buffer_FC()

    ##########################################
    # FC things

    def set_fc_bits_in_buffer(
            self,
            *, #noqa
            chip_index=0,
            part_bit_offset=0,
            field={"mask": 0, "length": 0, "offset": 0, "default": 0},
            value=0
    ):
        """Set function control bits in buffer."""
        # print(
        #     "chip_index={} "
        #     "part_bit_offset={} "
        #     "field={} "
        #     "value={} "
        #     "".format(
        #         chip_index,
        #         part_bit_offset,
        #         field,
        #         value
        #     )
        # )
        offset = part_bit_offset + field["offset"]
        # restrict value
        value &= field["mask"]
        # move value to position
        value = value << offset
        # calculate header start
        header_start = chip_index * self.CHIP_BUFFER_BYTE_COUNT
        # get chip header
        header = self._get_48bit_value_from_buffer(
            self._buffer_fc, header_start)
        # print("{:048b}".format(header))
        # 0xFFFFFFFFFFFF == 0b11111111111111111111111111111111....
        # create/move mask
        mask = field["mask"] << offset
        # clear
        header &= ~mask
        # set
        header |= value
        # write header back
        self._set_48bit_value_in_buffer(self._buffer_fc, header_start, header)

    def get_fc_bits_in_buffer(
            self,
            *, #noqa
            chip_index=0,
            part_bit_offset=0,
            field={"mask": 0, "length": 0, "offset": 0, "default": 0},
    ):
        """Get function control bits in buffer."""
        # print(
        #     "chip_index={} "
        #     "part_bit_offset={} "
        #     "field={} "
        #     "".format(
        #         chip_index,
        #         part_bit_offset,
        #         field,
        #     )
        # )
        offset = part_bit_offset + field["offset"]
        # calculate header start
        header_start = chip_index * self.CHIP_BUFFER_BYTE_COUNT
        # get chip header
        header = self._get_48bit_value_from_buffer(
            self._buffer_fc, header_start)
        # print("{:048b}".format(header))
        # 0xFFFFFFFFFFFF == 0b11111111111111111111111111111111....
        # create/move mask
        mask = field["mask"] << offset
        value = header & mask
        # move value to position
        value = value >> offset
        return value

    def _init_buffer_fc(self):
        for i in range(self.chip_count):
            for name, field in self._FC_FIELDS.items():
                self.set_fc_bits_in_buffer(
                    chip_index=i,
                    field=field,
                    value=field["default"]
                )

    def _print_buffer_fc__find_max_length(self):
        # find longest name
        # and prepare result
        max_length = {
            'name': 0,
            'value_bin': 0,
            'value_hex': 0,
        }
        for name, content in self._FC_FIELDS.items():
            if max_length['name'] < len(name):
                max_length['name'] = len(name)
            if max_length['value_bin'] < content["length"]:
                max_length['value_bin'] = content["length"]
            mask_as_hex_len = len("{:x}".format(content["mask"]))
            if max_length['value_hex'] < mask_as_hex_len:
                max_length['value_hex'] = mask_as_hex_len
        return max_length

    def _print_buffer_fc__prepare_results(self):
        result = {}
        # prepare result
        for name, field in self._FC_FIELDS.items():
            result[name] = []
            # add default
            result[name].append(field["default"])

        for i in range(self.chip_count):
            for name, field in self._FC_FIELDS.items():
                result[name].append(
                    self.get_fc_bits_in_buffer(
                        chip_index=i,
                        field=field
                    )
                )
        return result

    def print_buffer_fc(self):
        """Print internal function_command buffer content."""
        print("")
        result = self._print_buffer_fc__prepare_results()
        max_length = self._print_buffer_fc__find_max_length()

        # print
        ftemp = "{field_name:<" + str(max_length['name']) + "} | "
        print(ftemp.format(field_name='name/index'), end="")
        ftemp = "{field_value:^" + str(max_length['value_bin']) + "} | "
        # ftemp = "{field_value:>" + str(max_length['value_hex']) + "} | "
        print(ftemp.format(field_value='def'), end="")
        for index in range(self.chip_count):
            ftemp = "{field_value:^" + str(max_length['value_bin']) + "} | "
            # ftemp = "{field_value:^" + str(max_length['value_hex']) + "} | "
            print(ftemp.format(field_value=index), end="")
        print("")
        for name, content in result.items():
            ftemp = "{field_name:<" + str(max_length['name']) + "} | "
            print(ftemp.format(field_name=name), end="")
            for item in content:
                ftemp = (
                    "{field_value:>" +
                    str(max_length['value_bin']) +
                    "b} | "
                )
                # ftemp = (
                #     "{field_value:>" +
                #     str(max_length['value_hex']) +
                #     "x} | "
                # )
                print(ftemp.format(field_value=item), end="")
            print("")

    def set_fc_CC(
            self,
            chip_index=0,
            CCR=_FC_FIELDS['CCR']['default'],
            CCG=_FC_FIELDS['CCG']['default'],
            CCB=_FC_FIELDS['CCB']['default'],
    ):
        """Set color control for R, G, B."""
        self.set_fc_bits_in_buffer(
            chip_index=chip_index,
            field=self._FC_FIELDS["CCR"],
            value=CCR
        )
        self.set_fc_bits_in_buffer(
            chip_index=chip_index,
            field=self._FC_FIELDS["CCG"],
            value=CCG
        )
        self.set_fc_bits_in_buffer(
            chip_index=chip_index,
            field=self._FC_FIELDS["CCB"],
            value=CCB
        )

    def set_fc_CC_all(
            self,
            CCR=_FC_FIELDS['CCR']['default'],
            CCG=_FC_FIELDS['CCG']['default'],
            CCB=_FC_FIELDS['CCB']['default'],
    ):
        """Set color control for R, G, B for all chips."""
        for chip_index in range(self.chip_count):
            self.set_fc_CC(
                chip_index=chip_index,
                CCR=CCR,
                CCG=CCG,
                CCB=CCB,
            )

    def set_fc_BC(
            self,
            chip_index=0,
            BC=_FC_FIELDS['BC']['default'],
    ):
        """Set brightness control."""
        self.set_fc_bits_in_buffer(
            chip_index=chip_index,
            field=self._FC_FIELDS["BC"],
            value=BC,
        )

    def set_fc_BC_all(
            self,
            BC=_FC_FIELDS['BC']['default'],
    ):
        """Set brightness control for all chips."""
        for chip_index in range(self.chip_count):
            self.set_fc_BC(chip_index=chip_index, BC=BC)

    def set_fc_ESPWM(
            self,
            chip_index=0,
            enable=False,
    ):
        """Set ESPWM."""
        self.set_fc_bits_in_buffer(
            chip_index=chip_index,
            field=self._FC_FIELDS["ESPWM"],
            value=enable,
        )

    def set_fc_ESPWM_all(
            self,
            enable=False,
    ):
        """Set ESPWM for all chips."""
        for chip_index in range(self.chip_count):
            self.set_fc_ESPWM(chip_index=chip_index, enable=enable)

    ##########################################
    # GS things

    @staticmethod
    def _get_48bit_value_from_buffer(buffer, buffer_start):
        return (
            (buffer[buffer_start + 0] << 40) |
            (buffer[buffer_start + 1] << 32) |
            (buffer[buffer_start + 2] << 24) |
            (buffer[buffer_start + 3] << 16) |
            (buffer[buffer_start + 4] << 8) |
            buffer[buffer_start + 5]
        )

    @staticmethod
    def _set_48bit_value_in_buffer(buffer, buffer_start, value):
        if not 0 <= value <= 0xFFFFFFFFFFFF:
            raise ValueError(
                "value {} not in range: 0..0xFFFFFFFF"
                "".format(value)
            )
        # print("buffer_start", buffer_start, "value", value)
        # self._debug_print_buffer()
        buffer[buffer_start + 0] = (value >> 40) & 0xFF
        buffer[buffer_start + 1] = (value >> 32) & 0xFF
        buffer[buffer_start + 2] = (value >> 24) & 0xFF
        buffer[buffer_start + 3] = (value >> 16) & 0xFF
        buffer[buffer_start + 4] = (value >> 8) & 0xFF
        buffer[buffer_start + 5] = value & 0xFF

    # 32bit_value
    # def _get_32bit_value_from_buffer(self, buffer_start):
    #     return (
    #         (self._buffer[buffer_start + 0] << 24) |
    #         (self._buffer[buffer_start + 1] << 16) |
    #         (self._buffer[buffer_start + 2] << 8) |
    #         self._buffer[buffer_start + 3]
    #     )
    #
    # def _set_32bit_value_in_buffer(self, buffer_start, value):
    #     if not 0 <= value <= 0xFFFFFFFF:
    #         raise ValueError(
    #             "value {} not in range: 0..0xFFFFFFFF"
    #             "".format(value)
    #         )
    #     # print("buffer_start", buffer_start, "value", value)
    #     # self._debug_print_buffer()
    #     self._buffer[buffer_start + 0] = (value >> 24) & 0xFF
    #     self._buffer[buffer_start + 1] = (value >> 16) & 0xFF
    #     self._buffer[buffer_start + 2] = (value >> 8) & 0xFF
    #     self._buffer[buffer_start + 3] = value & 0xFF

    def _get_16bit_value_from_buffer(self, buffer_start):
        return (
            (self._buffer[buffer_start + 0] << 8) |
            self._buffer[buffer_start + 1]
        )

    def _set_16bit_value_in_buffer(self, buffer_start, value):
        assert 0 <= value <= 65535
        # print("buffer_start", buffer_start, "value", value)
        self._buffer[buffer_start + 0] = (value >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value & 0xFF

    @staticmethod
    def _convert_01_float_to_16bit_integer(value):
        """Convert 0..1 Float Value to 16bit (0..65535) Range."""
        # check if value is in range
        if not 0.0 <= value[0] <= 1.0:
            raise ValueError(
                "value[0] {} not in range: 0..1"
                "".format(value[0])
            )
        # convert to 16bit value
        return int(value * 65535)

    @classmethod
    def _convert_if_float(cls, value):
        """Convert if value is Float."""
        if isinstance(value, float):
            value = cls._convert_01_float_to_16bit_integer(value)
        return value

    @staticmethod
    def _check_and_convert(value):
        # check if we have float values
        if isinstance(value[0], float):
            # check if value is in range
            if not 0.0 <= value[0] <= 1.0:
                raise ValueError(
                    "value[0] {} not in range: 0..1"
                    "".format(value[0])
                )
            # convert to 16bit value
            value[0] = int(value[0] * 65535)
        else:
            if not 0 <= value[0] <= 65535:
                raise ValueError(
                    "value[0] {} not in range: 0..65535"
                    "".format(value[0])
                )
        if isinstance(value[1], float):
            if not 0.0 <= value[1] <= 1.0:
                raise ValueError(
                    "value[1] {} not in range: 0..1"
                    "".format(value[1])
                )
            value[1] = int(value[1] * 65535)
        else:
            if not 0 <= value[1] <= 65535:
                raise ValueError(
                    "value[1] {} not in range: 0..65535"
                    "".format(value[1])
                )
        if isinstance(value[2], float):
            if not 0.0 <= value[2] <= 1.0:
                raise ValueError(
                    "value[2] {} not in range: 0..1"
                    "".format(value[2])
                )
            value[2] = int(value[2] * 65535)
        else:
            if not 0 <= value[2] <= 65535:
                raise ValueError(
                    "value[2] {} not in range: 0..65535"
                    "".format(value[2])
                )

    ##########################################

    def set_pixel_16bit_value(self, pixel_index, value_r, value_g, value_b):
        """
        Set the value for pixel.

        This is a Fast UNPROTECTED function:
        no error / range checking is done.

        :param int pixel_index: 0..(pixel_count)
        :param int value_r: 0..65535
        :param int value_g: 0..65535
        :param int value_b: 0..65535
        """
        pixel_start = pixel_index * self.COLORS_PER_PIXEL
        buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_b >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_b & 0xFF
        buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_g >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_g & 0xFF
        buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_r >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_r & 0xFF

    def set_pixel_float_value(self, pixel_index, value_r, value_g, value_b):
        """
        Set the value for pixel.

        This is a Fast UNPROTECTED function:
        no error / range checking is done.

        :param int pixel_index: 0..(pixel_count)
        :param int value_r: 0..1
        :param int value_g: 0..1
        :param int value_b: 0..1
        """
        value_r = int(value_r * 65535)
        value_g = int(value_g * 65535)
        value_b = int(value_b * 65535)
        pixel_start = pixel_index * self.COLORS_PER_PIXEL
        buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_b >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_b & 0xFF
        buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_g >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_g & 0xFF
        buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_r >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_r & 0xFF

    def set_pixel_16bit_color(self, pixel_index, color):
        """
        Set color for pixel.

        This is a Fast UNPROTECTED function:
        no error / range checking is done.
        its a little bit slower as `set_pixel_16bit_value`

        :param int pixel_index: 0..(pixel_count)
        :param int color: 3-tuple of R, G, B;  0..65535
        """
        pixel_start = pixel_index * self.COLORS_PER_PIXEL
        buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (color[2] >> 8) & 0xFF
        self._buffer[buffer_start + 1] = color[2] & 0xFF
        buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (color[1] >> 8) & 0xFF
        self._buffer[buffer_start + 1] = color[1] & 0xFF
        buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (color[0] >> 8) & 0xFF
        self._buffer[buffer_start + 1] = color[0] & 0xFF

    def set_pixel_float_color(self, pixel_index, color):
        """
        Set color for pixel.

        This is a Fast UNPROTECTED function:
        no error / range checking is done.
        its a little bit slower as `set_pixel_16bit_value`

        :param int pixel_index: 0..(pixel_count)
        :param tuple/float color: 3-tuple of R, G, B;  0..1
        """
        # convert to 16bit int
        value_r = int(color[0] * 65535)
        value_g = int(color[1] * 65535)
        value_b = int(color[2] * 65535)
        # calculate pixel_start
        pixel_start = pixel_index * self.COLORS_PER_PIXEL
        # set values
        buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_b >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_b & 0xFF
        buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_g >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_g & 0xFF
        buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
        self._buffer[buffer_start + 0] = (value_r >> 8) & 0xFF
        self._buffer[buffer_start + 1] = value_r & 0xFF

    def set_pixel(self, pixel_index, value):
        """
        Set the R, G, B values for the pixel.

        this funciton hase some advanced error checking.
        it is much slower than the other provided 'bare' variants..
        but therefor gives clues to what is going wrong.. ;-)

        :param int pixel_index: 0..(pixel_count)
        :param tuple value: 3-tuple of R, G, B;
            each int 0..65535 or float 0..1
        """
        if 0 <= pixel_index < self.pixel_count:
            # print("pixel_index", pixel_index)
            # print("value", value)
            # convert to list
            value = list(value)
            # print("value", value)
            # print("rep:")
            # repr(value)
            # print("check length..")
            if len(value) != self.COLORS_PER_PIXEL:
                raise IndexError(
                    "length of value {} does not match COLORS_PER_PIXEL (= {})"
                    "".format(len(value), self.COLORS_PER_PIXEL)
                )
            # tested:
            # splitting up into variables to not need the list..
            # this is about 0.25ms slower..
            # value_r = value[0]
            # value_g = value[1]
            # value_b = value[2]

            # check if we have float values
            # this modifies 'value' in place..
            self._check_and_convert(value)

            # print("value", value)

            # update buffer
            # print("pixel_index", pixel_index, "value", value)
            # we change channel order here:
            # buffer channel order is blue, green, red
            pixel_start = pixel_index * self.COLORS_PER_PIXEL
            # self._set_channel_16bit_value(
            #     pixel_start + 0,
            #     value[2])
            # self._set_channel_16bit_value(
            #     pixel_start + 1,
            #     value[1])
            # self._set_channel_16bit_value(
            #     pixel_start + 2,
            #     value[0])
            # optimize2
            buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[2] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[2] & 0xFF
            buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[1] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[1] & 0xFF
            buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[0] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[0] & 0xFF
        else:
            raise IndexError(
                "index {} out of range [0..{}]"
                "".format(pixel_index, self.pixel_count-1)
            )

    def set_pixel_all_16bit_value(self, value_r, value_g, value_b):
        """
        Set the R, G, B values for all pixels.

        fast. without error checking.

        :param int value_r: 0..65535
        :param int value_g: 0..65535
        :param int value_b: 0..65535
        """
        for i in range(self.pixel_count):
            self.set_pixel_16bit_value(i, value_r, value_g, value_b)

    def set_pixel_all(self, color):
        """
        Set the R, G, B values for all pixels.

        :param tuple 3-tuple of R, G, B;  each int 0..65535 or float 0..1
        """
        for i in range(self.pixel_count):
            self.set_pixel(i, color)

    def set_all_black(self):
        """Set all pixels to black."""
        for i in range(self.pixel_count):
            self.set_pixel_16bit_value(i, 0, 0, 0)

    def set_channel(self, channel_index, value):
        """
        Set the value for the provided channel.

        :param int channel_index: 0..channel_count
        :param int value: 0..65535
        """
        if 0 <= channel_index < (self.channel_count):
            # check if values are in range
            if not 0 <= value <= 65535:
                raise ValueError(
                    "value {} not in range: 0..65535"
                )
            # temp = channel_index
            # we change channel order here:
            # buffer channel order is blue, green, red
            pixel_index_offset = channel_index % self.COLORS_PER_PIXEL
            if pixel_index_offset == 0:
                channel_index += 2
            if pixel_index_offset == 2:
                channel_index -= 2
            # print("{:>2} → {:>2}".format(temp, channel_index))
            buffer_index = channel_index * self.BUFFER_BYTES_PER_COLOR
            self._set_16bit_value_in_buffer(buffer_index, value)
            # self._set_16bit_value_in_buffer(
            #     self.COLORS_PER_PIXEL - channel_index, value)
        else:
            raise IndexError(
                "channel_index {} out of range (0..{})".format(
                    channel_index,
                    self.channel_count
                )
            )

    # Define index and length properties to set and get each channel as
    # atomic RGB tuples.  This provides a similar feel as using neopixels.
    def __len__(self):
        """Retrieve TLC5975 the total number of Pixels available."""
        return self.pixel_count

    def __getitem__(self, key):
        """
        Retrieve the R, G, B values for the provided channel as a 3-tuple.

        Each value is a 16-bit number from 0-65535.
        """
        if 0 < key < self.pixel_count:
            return (
                self._get_16bit_value_from_buffer(key + 0),
                self._get_16bit_value_from_buffer(key + 2),
                self._get_16bit_value_from_buffer(key + 4)
            )
        else:
            raise IndexError

    def __setitem__(self, key, value):
        """
        Set the R, G, B values for the pixel.

        this funciton hase some advanced error checking.
        it is much slower than the other provided 'bare' variants..
        but therefor gives clues to what is going wrong.. ;-)
        this shortcut is identicall to `set_pixel`

        :param int key: 0..(pixel_count)
        :param tuple 3-tuple of R, G, B;  each int 0..65535 or float 0..1
        """
        # for a more detailed version with all the debugging code and
        # comments look at set_pixel
        if 0 <= key < self.pixel_count:
            # convert to list
            value = list(value)

            if len(value) != self.COLORS_PER_PIXEL:
                raise IndexError(
                    "length of value {} does not match COLORS_PER_PIXEL (= {})"
                    "".format(len(value), self.COLORS_PER_PIXEL)
                )

            # this modifies value in place..
            self._check_and_convert(value)

            # update buffer
            # we change channel order here:
            # buffer channel order is blue, green, red
            pixel_start = key * self.COLORS_PER_PIXEL
            buffer_start = (pixel_start + 0) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[2] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[2] & 0xFF
            buffer_start = (pixel_start + 1) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[1] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[1] & 0xFF
            buffer_start = (pixel_start + 2) * self.BUFFER_BYTES_PER_COLOR
            self._buffer[buffer_start + 0] = (value[0] >> 8) & 0xFF
            self._buffer[buffer_start + 1] = value[0] & 0xFF
        else:
            raise IndexError(
                "index {} out of range [0..{}]"
                "".format(key, self.pixel_count-1)
            )

##########################################
