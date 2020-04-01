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
import sys
import os
import nasEncoder
import validations
from conversion_utility import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logger'))
import igniteLogger



def messageConversionJsonToByte(json_input_message, type_of_request, json_msg_grammar, json_field_grammar,
                                validation_flag):
    try:

        converted_message = ""

        if (type_of_request not in json_msg_grammar):

            return "Parsing Failed, type of request not in the mentioned message grammar"

        else:

            if (validation_flag == 'Y'):

                check_validation, missing_list = validations.checkMandatoryFields(json_msg_grammar, type_of_request,
                                                                                  json_input_message)

                if (not check_validation):
                    return "Mandatory fields missing : " + str(missing_list)

            request_fields = json_msg_grammar[type_of_request].keys()

            for fields in request_fields:
                converted_message = converted_message + joinMsgFunction(json_input_message,
                                                                        json_msg_grammar[type_of_request][fields],
                                                                        json_field_grammar) + " "

            encoded_list = converted_message.split()

            for index in range(0, len(encoded_list)):

                encoded_list[index] = encoded_list[index].replace("0x", "")

                if len(encoded_list[index]) == 1:
                    encoded_list[index] = str(0) + str(encoded_list[index])

            return " ".join(encoded_list)



    except Exception as error:

        igniteLogger.logger.error(f"{str(error)} exception occured")


def joinMsgFunction(json_input_message, field_list, msg_fields):
    try:

        combined_value = []
        for fields in field_list:

            if ("dict" in str(type(fields))):

                for key in fields.keys():

                    if ('union_mf' in key):

                        combined_value.append(unionMsgFunction(fields['union_mf'], json_input_message, msg_fields))

                    elif ('join_mf' in key):

                        combined_value.append(joinMsgFunction(json_input_message, fields['join_mf'], msg_fields))

                    elif ('join_sf' in key):

                        combined_value.append(joinMsgFunction(json_input_message, fields['join_sf'], msg_fields))

                    elif ('union_sf' in key):

                        combined_value.append(unionMsgFunction(fields[key], json_input_message, msg_fields))

            else:

                parsed_value = parseMsgFields(fields, json_input_message, msg_fields)

                if (parsed_value):
                    combined_value.append(parsed_value)

        return " ".join(combined_value)



    except Exception as error:

        igniteLogger.logger.error("ERROR : " f"{str(error)} exception occurred")


def unionMsgFunction(field_list, json_input_message, msg_fields):
    try:

        combined_value = []

        for fields in field_list:

            if ("dict" in str(type(fields))):

                for key in fields.keys():

                    if ("join_mf" in field):

                        combined_value.append(json_input_message,
                                              unionMsgFunction(fields['join_mf'], json_input_message, msg_fields))

                    elif ('union_mf' in key):

                        combined_value.append(unionMsgFunction(fields['union_mf'], json_input_message, msg_fields))

                    elif ('join_sf' in key):

                        combined_value.append(joinMsgFunction(json_input_message, fields['join_sf'], msg_fields))

                    elif ('union_sf' in key):

                        combined_value.append(unionMsgFunction(fields[key], json_input_message, msg_fields))

            else:

                parsed_value = parseMsgFields(fields, json_input_message, msg_fields)

                if (parsed_value):
                    combined_value.append(parsed_value)

        final_value = '0x0'

        for value in combined_value:

            if ('str' not in str(type(value))):
                value = str(value)

            final_value = hex(int(final_value, 16) | int(value, 16))

        return final_value



    except Exception as error:

        igniteLogger.logger.error("ERROR : " f"{str(error)} exception occurred")


def parseMsgFields(field_name, json_input_message, json_msg_fields):
    try:

        final_value = ""

        field_grammar = json_msg_fields[field_name]

        if (field_name not in json_input_message.keys() and nasEncoder.validationFlag == 'N'):

            field_keys = field_grammar.keys()

            end_bit = int(field_grammar['end_bit']) if ('end_bit' in field_keys) else 0

            max_size = int(field_grammar['max_size']) if ('max_size' in field_keys) else 1

            min_size = int(field_grammar['min_size']) if ('min_size' in field_keys) else 1

            nasEncoder.TYPE_ID = str(field_grammar['type_id']) if ('type_id' in field_keys) else "0x00"

            format_value = field_grammar['format']

            encoded_value = [];

            for i in range(0, max_size):
                encoded_value.append("00")

            return formatCheck(encoded_value, format_value, max_size, min_size)

        if (field_name in json_input_message.keys()):

            field_keys = field_grammar.keys()

            field_value = json_input_message[str(field_name)]

            end_bit = int(field_grammar['end_bit']) if ('end_bit' in field_keys) else 0

            max_size = int(field_grammar['max_size']) if ('max_size' in field_keys) else 1

            min_size = int(field_grammar['min_size']) if ('min_size' in field_keys) else 1

            nasEncoder.TYPE_ID = str(field_grammar['type_id']) if ('type_id' in field_keys) else "0x00"

            if ('start_bit' in field_keys):

                start_bit = int(field_grammar['start_bit'])

            else:

                start_bit = int(max_size * 8 - 1)

            format_value = field_grammar['format']

            if ('join_sf' in field_keys):

                if (nasEncoder.validationFlag == 'Y'):
                    validations.checkMandatorySubFields(json_msg_fields, json_input_message, field_name)

                final_value = joinMsgFunction(json_input_message[field_name], field_grammar['join_sf'],
                                              json_msg_fields)


            elif ('union_sf' in field_keys):

                if (nasEncoder.validationFlag == 'Y'):
                    validations.checkMandatorySubFields(json_msg_fields, json_input_message, field_name)

                final_value = unionMsgFunction(field_grammar['union_sf'], json_input_message[field_name],
                                               json_msg_fields)



            else:

                if ('json_to_byte' in field_keys) and (field_grammar['json_to_byte']):

                    json_to_byte_map = field_grammar['json_to_byte']

                    map_value = int(json_to_byte_map[field_value]) if (field_value in json_to_byte_map.keys()) else -1

                    final_value = leftShiftValues(map_value, start_bit, end_bit) if (end_bit != 0) else map_value

                    final_value = hex(final_value)

                else:

                    json_type = field_grammar['json_type']

                    byte_type = field_grammar['byte_type']

                    if (json_type == 'num'):

                        field_value = int(field_value)

                        if (start_bit == 0 and end_bit == 0):

                            final_value = field_value

                        else:

                            final_value = leftShiftValues(field_value, start_bit, end_bit)

                        final_value = hex(final_value)


                    elif (json_type == 'str'):

                        final_value = stringToHexConversion(field_value)

            nasEncoder.TYPE_ID = str(field_grammar['type_id']) if ('type_id' in field_keys) else "0x00"

            final_value = byteConversion(final_value, max_size)

            final_value = (formatCheck(final_value, format_value, max_size, min_size))

            if (len(str(final_value)) == 1):
                final_value = str(str(0) + str(final_value))

            return final_value



        elif (field_grammar['type'] == 'O') and (field_name not in json_input_message.keys()):

            return ""



        else:

            igniteLogger.logger.error(f"Mandatory Feild {field_name} missing")



    except Exception as error:

        igniteLogger.logger.error("ERROR : " f"{str(error)} exception occurred")

