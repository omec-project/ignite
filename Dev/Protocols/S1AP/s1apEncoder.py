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

import asn1tools
import json
import time
import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'NAS', 'Encoder'))
import nasEncoder

IEGRAMMAR = {"dL-transportLayerAddress": "BIT STRING", "transportLayerAddress": "BIT STRING", "eNB-ID": "CHOICE",
             "Cause": "CHOICE","TargetID":"CHOICE","macroENB-ID":"BIT STRING"}
IELENGTH = {"dL-transportLayerAddress": 32, "transportLayerAddress": 32,"macroENB-ID":20}

start = time.time()


def processList(key, list_data, asn_object):
    data_to_asn = []
    for lists in range(len(list_data)):
        lists_data = list_data[lists]
        if type(lists_data) == dict:
            if "id" in lists_data:
                processed_dict = processDict(key, lists_data, asn_object)
                lists_data['value'] = processed_dict
                data_to_asn.append(lists_data)
            else:
                if type(lists_data) == dict:
                    processed_dict = processDict(key, lists_data, asn_object)
                    return processed_dict
    encoded_data = asnEncoding(key, data_to_asn, asn_object)
    return encoded_data

def processDict(dict_key, dict_data, asn_object):
    for key, value in dict_data.items():
        if "id" in dict_data:
            dict_data = dict_data['value']
            for data_key, data_value in dict_data.items():
                if type(data_value) == dict:
                    processed_dict = processDict(data_key, data_value, asn_object)
                    encoded_data = asnEncoding(data_key, data_value, asn_object)
            return encoded_data
        # Check ie_s in dictionary containing ie_s of type BIT STRING and CHOICE
        if key in IEGRAMMAR:
            # If key is of type BIT STRing convert value as tuple(bytes,int)
            if IEGRAMMAR[key] == "BIT STRING":
                processed_string = processString(value)
                dict_data[key] = (processed_string, IELENGTH[key])
            # If key is of type CHOICE convert value as tuple(str,object)
            elif IEGRAMMAR[key] == "CHOICE":
                if type(value) == dict:
                    processed_dict = processDict(key, value, asn_object)
                    for processed_dict_key, processed_dict_value in processed_dict.items():
                        dict_data[key] = (processed_dict_key, processed_dict_value)
        else:
            if type(value) == str:
                processed_string = processString(value)
                dict_data[key] = processed_string
            elif type(value) == int:
                if dict_key in IEGRAMMAR:
                    if IEGRAMMAR[dict_key] == "CHOICE":
                        return (key, value)
            elif type(value) == dict:
                processed_dict = processDict(key, value, asn_object)
            elif type(value) == list:
                processed_list = processList(key, value, asn_object)
                dict_data[key] = list(processed_list.values())

    return dict_data


# Convert string to bytesarray
def processString(data):
    string_data = str(data)
    bytes_array = bytes.fromhex(string_data)
    processed_string = (bytes_array)
    return processed_string


# NAS Encoder and return the encoded value
def encodeNasPdu(key, data, value, asn_object, ctxtData={}):
    protocol = "5G"
    version = "v1"
    request_type = value
    field_validation_flag = "Y"
    nas = nasEncoder.encoder(protocol, version, request_type, data, field_validation_flag, ctxtData)
    bytes_array = bytes.fromhex(nas)
    nas_encoded = asnEncoding(key, bytes_array, asn_object)
    return nas_encoded


def asnEncoding(ies_key, ies_parameter, asn_object):
    encoded_data = asn_object.encode(ies_key, ies_parameter)
    return encoded_data


def s1apEncoding(data, asn_object, nasData={}, ctxtData={}):
    try:
        list_of_ies = {}
        s1ap_pdu_msge = data["S1AP-PDU"]
        for s1ap_pdu_key, s1ap_pdu_value in s1ap_pdu_msge.items():
            s1ap_elementarys = s1ap_pdu_value['value']
            for elementarys_key, elementarys_value in s1ap_elementarys.items():
                list_of_ies_parameter = elementarys_value['protocolIEs']
                for index in range(len(list_of_ies_parameter)):
                    ie_s = list_of_ies_parameter[index]
                    ie_parameters = ie_s['value']
                    for ie_parameter_key, ie_parameter_value in list(ie_parameters.items()):
                        # If key is NAS-PDU it will call nas_pdu API
                        if ie_parameter_key == "NAS-PDU":
                            encoded_data = encodeNasPdu(ie_parameter_key, nasData, ie_parameter_value, asn_object, ctxtData)
                            list_of_ies_parameter[index]['value'] = encoded_data

                        elif type(ie_parameter_value) == int:
                            encoded_data = asnEncoding(ie_parameter_key, ie_parameter_value, asn_object)
                            ie_s['value'] = encoded_data

                        elif type(ie_parameter_value) == list:
                            if ie_parameter_key in IEGRAMMAR and len(ie_parameter_value) > 1:
                                multi_tac = []
                                for x in ie_parameter_value:
                                    encode = []
                                    encode.append(x)
                                    processed_list = processList(ie_parameter_key, encode, asn_object)
                                    for value in processed_list.values():
                                        multi_tac.append(value)
                                    encoded_data = asnEncoding(ie_parameter_key, multi_tac, asn_object)
                                    ie_s['value'] = encoded_data
                            else:
                                processed_list = processList(ie_parameter_key, ie_parameter_value, asn_object)
                                if type(processed_list) == dict:
                                    dict_list = list(processed_list.values())
                                    encoded_data = asnEncoding(ie_parameter_key, dict_list, asn_object)
                                    ie_s['value'] = encoded_data
                                else:
                                    ie_s['value'] = processed_list
                        elif type(ie_parameter_value)== str:
                            ie_s['value'] = processString(ie_parameter_value)
                        elif type(ie_parameter_value) == dict:
                            if ie_parameter_key in IEGRAMMAR:
                                if IEGRAMMAR[ie_parameter_key] == "CHOICE":
                                    processed_dict = processDict(ie_parameter_key, ie_parameter_value, asn_object)
                                    if type(processed_dict) != tuple:
                                        for key, value in processed_dict.items():
                                            choice_data = (key, value)

                                        encoded_data = asnEncoding(ie_parameter_key, choice_data, asn_object)
                                    else:
                                        encoded_data = asnEncoding(ie_parameter_key, processed_dict, asn_object)

                                    ie_s['value'] = encoded_data
                            else:
                                processed_dict = processDict(ie_parameter_key, ie_parameter_value, asn_object)
                                encoded_data = asnEncoding(ie_parameter_key, processed_dict, asn_object)
                                ie_s['value'] = encoded_data

                list_of_ies['protocolIEs'] = list_of_ies_parameter

        elementarys_key = elementarys_key
        elementarys_key = elementarys_key[0].upper() + elementarys_key[1:-1] + elementarys_key[-1]
        encoded_data = asnEncoding(elementarys_key, list_of_ies, asn_object)
        s1ap_pdu_value['value'] = encoded_data
        s1ap_pdu = (s1ap_pdu_key, s1ap_pdu_value)
        encoded_data = asnEncoding("S1AP-PDU", s1ap_pdu, asn_object)
        s1ap_pdu_hexa_value = encoded_data.hex()

        return s1ap_pdu_hexa_value

    except Exception as e:
        igniteLogger.logger.info("Printing exception : "f"{e}")


