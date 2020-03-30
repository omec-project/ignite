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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logger'))
import igniteLogger

HOME_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'Grammar')
OUTPUT = HOME_DIRECTORY + "/../Output/encoded_message.txt"

validationFlag = "Y"
TYPE_ID = "0x00"

def checkRequest(request_type):
    if request_type in REQUEST_TYPE:
        return REQUEST_TYPE[request_type]
    else:
        return "other"


def encoder(protocol,version,request_type,nasData,field_validation_flag):

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

        output_byte = fve.messageConversionJsonToByte(nasData, type_of_request, json_msg_grammar, json_field_grammar,validationFlag)
        encoded_output.write(str(output_byte))
        encoded_output.close()
        return str(output_byte)

    except Exception as error:
        igniteLogger.logger.info("Printing exception : "f"{e}")



