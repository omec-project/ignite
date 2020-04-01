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

import os
import nasEncoder
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logger'))
import igniteLogger

def validation(HOME_DIRECTORY, PATH, protocol, version, MESSAGE, FIELD_GRAMMAR):
    if not (folderValidation(HOME_DIRECTORY, protocol)):
        raise Exception("Specified Protocol Not Available")

    path = HOME_DIRECTORY + "/" + protocol

    if not (folderValidation(path, version)):
        raise Exception("Specified Version Not Available")

    path = HOME_DIRECTORY + "/" + protocol + "/" + version

    if not (fileValidation(PATH, MESSAGE)):
        raise Exception("Specified Message Grammar file Not Available")

    if not (fileValidation(PATH, FIELD_GRAMMAR)):
        raise Exception("Specified Field Grammar file Not Available")


def folderValidation(path, folder):
    try:

        folder_list = []

        for r, d, f in os.walk(path):
            folder_list.append(d)

        if (folder in folder_list[0]):

            return True

        else:

            return False



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)} exception occurred during folder validation")


def fileValidation(path, file):
    try:

        file_list = []

        for r, d, f in os.walk(path):
            file_list.append(f)

        if (file in file_list[0]):

            return True

        else:

            return False



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)} exception occurred during folder validation")


def checkMandatoryFields(msg_grammar, type_of_request, json_input_msg):
    try:

        mandatory_list = msg_grammar[type_of_request]['M']

        for field_list in mandatory_list:

            if ("dict" in str(type(field_list))):

                for key, value in field_list.items():

                    if ('list' in str(type(value))):

                        for i in value:

                            if not (i in json_input_msg):
                                return False, field_list

                    else:

                        if not (value in json_input_msg):
                            return False, field_list

            else:

                if not (field_list in json_input_msg):
                    return False, field_list

        return True, ''



    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)} exception occurred during folder validation")


def checkMandatorySubFields(json_msg_field_grammar, json_input_msg, field_name):
    try:

        sub_fields = []

        if ('join_sf' in json_msg_field_grammar[field_name].keys()):

            sub_fields = json_msg_field_grammar[field_name]['join_sf']

        elif ('union_sf' in json_msg_field_grammar[field_name].keys()):

            sub_fields = json_msg_field_grammar[field_name]['union_sf']

        else:

            pass

        mandatory_list = []

        for field in sub_fields:

            if ('dict' not in str(type(field))) and ('list' not in str(type(field))):

                if (json_msg_field_grammar[field]['type'] == 'M'):
                    mandatory_list.append(field)

        input_sub_fields = json_input_msg[field_name].keys()

        for field in mandatory_list:

            if (field not in input_sub_fields):
                igniteLogger.logger.error(f"Mandatory field {field} missing")




    except Exception as error:

        igniteLogger.logger.error("ERROR : "f"{str(error)} exception occurred during folder validation")
