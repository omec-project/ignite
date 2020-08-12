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
import os, sys
import binascii
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from protocolMessageTypes import ProtocolMessageTypes as mt

rat_type_gtp_map={
        "UTRAN":1,
        "GERAN":2,
        "WLAN":3,
        "GAN":4,
        "HSPA Evolution":5,
        "EUTRAN":6,
        "Virtual":7,
        "EUTRAN-NB-IoT":8
        }

interface_type_gtp_map={
        "S1-U eNodeB GTP-U":0,
        "S1-U SGW GTP-U":1,
        "S12 RNC GTP-U":2,
        "S12 SGW GTP-U":3,
        "S11 MME GTP-C":10,
        "S11/S4 SGW GTP-C":11
        }

gtpMessageDict={
    32:"create_session_request",
    33:"create_session_response",
    34:"modify_bearer_request",
    35:"modify_bearer_response",
    36:"delete_session_request",
    37:"delete_session_response",
    170:"release_bearer_request",
    171:"release_bearer_response",
    176:"downlink_data_notification",
    177:"downlink_data_notification_ack",
    178:"downlink_data_notification_failure"
    }

gtpRespReqDict={
    "create_session_response":"create_session_request",
    "modify_bearer_response":"modify_bearer_request",
    "delete_session_response":"delete_session_request",
    "release_bearer_response":"release_bearer_request"
    }

gtpInitialMessagesList=[mt.downlink_data_notification.name]


def taiEcgiTohex(value):
    hexVal=""
    mcc=value["mcc"]
    mnc=value["mnc"]
    hexVal+=hex(int(mcc[1]))[-1]+hex(int(mcc[0]))[-1]
    if len(mnc)==3:
        hexVal+=hex(int(mnc[2]))[-1]
    else:
        hexVal+=hex(15)[-1]
    hexVal+=hex(int(mcc[2]))[-1]+hex(int(mnc[1]))[-1]+hex(int(mnc[0]))[-1]
    return hexVal

def ipadressToHex(value):
    tl_list = []
    ip_list = value.split(".")
    for x in ip_list:
        tl_list.append(int(x))
    address = binascii.hexlify(bytearray(tl_list))
    final_address = str(address.decode())
    return final_address

def updateGtpIp(dictToUpdate, ipAddress):
    updated_dict = dictToUpdate
    matched = "false"

    for key, value in dictToUpdate.items():

        if key == 'ipv4address':
            matched = "true"
            keywordPatternMatches = re.search('\$SgwIpAddress', value)
            if keywordPatternMatches:
                dictToUpdate[key] = ipAddress

        elif isinstance(value, dict):
            updatedDict_1, matched_1 = updateGtpIp(value, ipAddress)
            if matched_1 == "true":
                matched = matched_1
                value = updatedDict_1
                dictToUpdate[key] = value

        elif isinstance(value, list):
            for i in range (len(value)):
                if isinstance(value[i], dict):
                    updatedDict_2, matched_2 = updateGtpIp(value[i], ipAddress)
                    if matched_2 == "true":
                        matched = matched_2
                        value[i] = updatedDict_2
                        dictToUpdate[key]= value

    updated_dict = dictToUpdate
    return updated_dict, matched

