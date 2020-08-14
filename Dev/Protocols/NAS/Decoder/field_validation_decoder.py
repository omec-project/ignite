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


import json
import os
from conversion_utility_decoder import *

HOME_DIR = os.path.dirname(__file__)
MESSAGE_GRAMMAR = os.path.join(HOME_DIR, '..', 'Grammar', 'message_grammar.json')
FEILD_GRAMMAR = os.path.join(HOME_DIR, '..', 'Grammar', 'field_grammar.json')


def convertByteToJson(output_list, msg_type):
    message = open(MESSAGE_GRAMMAR, 'r')
    msg = json.load(message)
    message.close()

    message_fields = open(FEILD_GRAMMAR, 'r')
    msg_fields = json.load(message_fields)
    message_fields.close()

    decoded_output = " "
    msg_structure = []

    for key, value in msg[msg_type].items():

        if (type(value) is list):

            if len(value) > 0:

                for field in value:
                    msg_structure.append(field)

        else:

            msg_structure.append(value)

    count = 0

    for field in msg_structure:

        field_count = len(msg_structure)

        if ("union_mf" in field):

            for sub_field in field["union_mf"]:

                sub_field_grammar = msg_fields[sub_field]

                format_of_field = sub_field_grammar['format']

                if not (checkOptional(format_of_field, sub_field_grammar, output_list)):
                    count += 1
                    continue

                decoded_output = decoded_output + decoder(sub_field_grammar, output_list)

                if count < (field_count - 1):
                    decoded_output = decoded_output + ","

            output_list.pop(0)

        elif ("join_mf" in field):

            for sub_field in field["join_mf"]:

                sub_field_grammar = msg_fields[sub_field]

                format_of_field = sub_field_grammar['format']

                if not (checkOptional(format_of_field, sub_field_grammar, output_list)):
                    continue

                decoded_output = decoded_output + decoder(sub_field_grammar, output_list)

                output_list.pop(0)

        else:

            msg_field_grammar = msg_fields[field]

            format_of_field = msg_field_grammar['format']

            if not (checkOptional(format_of_field, msg_field_grammar, output_list)):
                count += 1
                continue

            num_of_bytes_to_pop = msg_field_grammar["max_size"] if ("max_size" in msg_field_grammar) else 1

            if ('L' in msg_field_grammar["format"]):

                if (msg_field_grammar["format"] == "LV"):
                    num_of_bytes_to_pop = int(output_list[0], 16)
                elif (msg_field_grammar["format"] == "TLV"):
                    num_of_bytes_to_pop = int(output_list[1], 16)

                elif (msg_field_grammar["format"] == "LV-E"):
                    num_of_bytes_to_pop = int(output_list[0] + output_list[1], 16)
                elif (msg_field_grammar["format"] == "TLV-E"):
                    num_of_bytes_to_pop = int(output_list[1] + output_list[2], 16)

            decoded_output = decoded_output + decoder(msg_field_grammar, output_list)

            if count < (field_count - 1):
                decoded_output = decoded_output + ","

            if (output_list):

                for i in range(0, num_of_bytes_to_pop):
                    output_list.pop(0)

        count += 1

    if decoded_output[-1] == ",":
        decoded_output = decoded_output[0:len(decoded_output) - 1]

    return ("{" + decoded_output + "}")


def decoder(msg_field_grammar, output_list):
    final_value = ""
    decoded_value = ""

    max_size = msg_field_grammar["max_size"] if ("max_size" in msg_field_grammar) else 1

    byte_to_json = msg_field_grammar["byte_to_json"] if ("byte_to_json" in msg_field_grammar) else {}

    end_bit = msg_field_grammar["end_bit"] if ("end_bit" in msg_field_grammar) else 0

    json_type = msg_field_grammar["json_type"] if ("json_type" in msg_field_grammar) else ""

    name = msg_field_grammar["name"]

    final_value = final_value + '"' + name + '"' + " : "

    if ("start_bit" in msg_field_grammar):

        start_bit = int(msg_field_grammar["start_bit"])




    else:

        start_bit = max_size * 8 - 1

    format_value = msg_field_grammar["format"]

    if ("join_sf" in msg_field_grammar):

        joined_sub_fields = msg_field_grammar["join_sf"]

        if ('L' in msg_field_grammar["format"]):

            if msg_field_grammar["format"] == "LV":  # Length indicator is 1 octet long

                length = int(output_list[0], 16)
                output_list.pop(0)

            elif msg_field_grammar["format"] == "TLV":  # Length indicator is in 2nd octet

                length = int(output_list[1], 16)

                for i in range(0, 2):
                    output_list.pop(0)



            elif msg_field_grammar["format"] == "LV-E" or msg_field_grammar[
                "format"] == "TLV-E":  # Length indicator is 2 octet long

                length = (int(output_list[0], 16) << 8) | (int(output_list[1], 16))

                for i in range(0, 2):
                    output_list.pop(0)

        else:

            length = msg_field_grammar["max_size"]

        sub_encoded_list = []

        for i in range(0, length):
            sub_encoded_list.append(output_list[i])

        final_value = final_value + "{"
        decoded_value = join(joined_sub_fields, sub_encoded_list)

        decoded_value = decoded_value + "}"

    elif ("union_sf" in msg_field_grammar):

        for sub_field in field["union_sf"]:
            sub_field_grammar = msg_fields[sub_field]

            decoded_output = decoded_output + decoder(sub_field_grammar, output_list)

    else:

        output_field = ""

        if (max_size > 1):

            if ('L' in msg_field_grammar["format"]):
                length = int(output_list[0], 16)

            for i in range(0, max_size):
                output_field = output_field + output_list[i]

            start_bit = (max_size * 8) - 1

        elif json_type == "str" and start_bit > 7:

            for i in range(0, len(output_list)):
                output_field = output_field + output_list[i]

            output_field = output_field.rstrip()

        else:

            output_field = output_list[0]

        if (byte_to_json):

            decoded_value = byteToJsonConversion(end_bit, start_bit, output_field, byte_to_json, max_size)

        else:

            if (end_bit == 0 and start_bit == 0 and json_type == "num" and max_size == 0):

                integer_value = str(int(output_field[0], 16))
                decoded_value = str(integer_value)

            elif json_type == "str":

                decoded_value = hexstrToAscii(output_field)

            else:

                decoded_value = str(byteToJsonConversion(end_bit, start_bit, output_field, byte_to_json, max_size))

    if json_type == "str":

        final_value = final_value + '"' + decoded_value + '"'

    else:

        final_value = final_value + decoded_value

    return final_value


def join(joined_sub_fields, output_list):
    message_fields = open(FEILD_GRAMMAR, 'r')
    msg_fields = json.load(message_fields)
    message_fields.close()
    decoded_output = ""
    count = 0

    for field in joined_sub_fields:

        num_of_fields = len(joined_sub_fields)

        if type(field) == str:

            msg_field_grammar = msg_fields[field]

            if not (checkOptional(msg_field_grammar["format"], msg_field_grammar, output_list)):
                count += 1
                continue

        if ("union_sf" in field):

            subFieldCount = 0
            num_of_subFields = len(field["union_sf"])

            for sub_field in field["union_sf"]:

                sub_field_grammar = msg_fields[sub_field]

                if decoded_output != "" and decoded_output[-1] != ",":
                    decoded_output = decoded_output + ","

                decoded_output = decoded_output + decoder(sub_field_grammar, output_list)

                if subFieldCount < (num_of_subFields - 1):
                    decoded_output = decoded_output + ","

                subFieldCount += 1

            output_list.pop(0)

        else:

            msg_field_grammar = msg_fields[field]

            json_type = msg_field_grammar["json_type"] if ("json_type" in msg_field_grammar) else ""

            num_of_bytes_to_pop = msg_field_grammar["max_size"] if ("max_size" in msg_field_grammar) else 1

            if ('L' in msg_field_grammar["format"]):

                if msg_field_grammar["format"] == "LV":

                    num_of_bytes_to_pop = int(output_list[0], 16)

                elif msg_field_grammar["format"] == "TLV":

                    num_of_bytes_to_pop = int(output_list[1], 16)

            elif json_type == "str":

                num_of_bytes_to_pop = len(output_list)

            if decoded_output != "" and decoded_output[-1] != ",":
                decoded_output = decoded_output + ","

            decoded_output = decoded_output + decoder(msg_field_grammar, output_list)

            if count < (num_of_fields - 1):
                decoded_output = decoded_output + ","

            for i in range(0, num_of_bytes_to_pop):
                output_list.pop(0)

        count += 1

    return decoded_output
