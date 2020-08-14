#
# Copyright (c) 2019, Infosys Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import nasEncoder
import os, sys

currDir = os.path.dirname(__file__)
sys.path.append(os.path.join(currDir, '..', '..', '..', 'Logger'))
import igniteLogger


# Conversion Of String to Hexadecimal

def stringToHexConversion(string_value):
    try:

        converted_byte_array = []

        for letter in string_value:
            converted_byte_array.append(hex(ord(letter)))

        converted_byte_array.insert(0, str(len(string_value)))
        converted_byte_array = " ".join(val for val in converted_byte_array)

        return converted_byte_array



    except Exception as error:

        igniteLogger.logger.error("ERROR : " f"{str(error)} exception occurred")

        # sys.exit()


# Left Shift ()

def leftShiftValues(digit, start_bit, end_bit):
    try:

        nibble_value = end_bit

        shifted_value = digit << nibble_value

        return shifted_value



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)}  exception occurred")

        # sys.exit()


def formatCheck(final_value, format_value, max_size, min_size):
    try:

        if ('str' in str(type(final_value))):

            hex_list = final_value.split(" ")

            length_of_list = len(hex_list)

            final_value = hex_list

        else:

            length_of_list = len(final_value)

        length = hex(length_of_list)

        if ('L' in format_value):
            final_value.insert(0, str(length))

        if ('T' in format_value):
            final_value.insert(0, str(nasEncoder.TYPE_ID))

        final_value = " ".join(final_value)

        return str(final_value)



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)}  exception occurred")

        # sys.exit()


def byteConversion(final_value, max_size):
    try:

        if (len(final_value.split(" ")) > 1):
            return final_value

        integer_value = int(final_value, 16)

        no_of_bytes = max_size * 8

        binary_value = format(integer_value, '0' + str(no_of_bytes) + 'b')

        final_value = ""

        count = 0

        for i in range(0, (max_size * 2)):

            bin_value = ""

            for j in range(0, 4):
                bin_value = bin_value + binary_value[count]

                count += 1

            converted_int = int(bin_value, 2)

            hex_value = str(hex(converted_int)).replace("0x", "")

            if (count % 8 == 0):

                final_value = final_value + str(hex_value) + " "

            else:

                final_value = final_value + str(hex_value)

        return final_value.strip(" ")



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)}  exception occurred")

        # sys.exit()
