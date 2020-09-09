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
import field_validation_encoder as fve
from check_request_type import REQUEST_TYPE
import validations
from _ast import Or

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logger'))
import igniteLogger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Util'))
import secUtils as su

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Decoder'))
import field_validation_decoder as fvd

HOME_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'Grammar')
OUTPUT = HOME_DIRECTORY + "/../Output/encoded_message.txt"

validationFlag = "Y"
TYPE_ID = "0x00"

def checkRequest(request_type):
    if request_type in REQUEST_TYPE:
        return REQUEST_TYPE[request_type]
    else:
        return "other"


def encoder(protocol,version,request_type,nasData,field_validation_flag, ctxtData={}):

    try:
        global validationFlag
        MESSAGE = "message_grammar.json"
        FIELD_GRAMMAR = "field_grammar.json"
        PATH = HOME_DIRECTORY + "/"

        #validate = validations.validation(HOME_DIRECTORY,PATH,protocol,version,MESSAGE,FIELD_GRAMMAR)
        type_of_request = checkRequest(request_type)

        MESSAGE = PATH + MESSAGE
        FIELD_GRAMMAR = PATH + FIELD_GRAMMAR
        validationFlag = field_validation_flag

        encoded_output = open(OUTPUT, 'w')
        message = open(MESSAGE, 'r')
        json_msg_grammar = json.load(message)
        message.close()

        field_grammer = open(FIELD_GRAMMAR, 'r')
        json_field_grammar = json.load(field_grammer)
        field_grammer.close()

        output_byte = fve.messageConversionJsonToByte(nasData, type_of_request, json_msg_grammar, json_field_grammar, validationFlag)

        if nasData['security_header_type'] != 'plain_nas_message_not_security_protected':
            if nasData['security_header_type'] == 'security_header_service_request':
                mac_data_str = output_byte.replace(' ', '')
                mac_data_bytes = (bytearray.fromhex(mac_data_str))[:2]
                mac = su.calculateMac(ctxtData['SEC_CXT']['INTEGRITY_KEY'],
                                      nasData['ksi_sequence_number']['sequence_number_service_req'],
                                      0,
                                      0,
                                      mac_data_bytes,
                                      len(mac_data_bytes))
                output_byte = output_byte[:5] + mac[5:]
            else:
                mac_data_str = output_byte.replace(' ', '')
                mac_data_bytes = (bytearray.fromhex(mac_data_str))[5:]
                mac = su.calculateMac(ctxtData['SEC_CXT']['INTEGRITY_KEY'],
                                      nasData['sequence_number'],
                                      0,
                                      0,
                                      mac_data_bytes,
                                      len(mac_data_bytes))
                output_byte = output_byte[:3] + mac + output_byte[14:]
        
        encoded_output.write(str(output_byte))
        encoded_output.close()
        return str(output_byte)

    except Exception as error:
        igniteLogger.logger.info("Printing exception : "f"{e}")



