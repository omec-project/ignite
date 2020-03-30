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

import binascii
import json
from array import *
import os
import sys,random
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Logger'))
import igniteLogger

configuration_file = os.path.join(os.path.dirname(__file__), 'configuration.json')
with open(configuration_file) as configuration:
            config_file=json.loads(configuration.read())
			
url={
"diameter_buff_clr_url":"http://"+str(config_file["diameter"]["ignite_ip"])+":"+str(config_file["diameter"]["tc_port"])+"/clearMessageBuffer",
"gtp_buff_clr_url":"http://"+str(config_file["gtp"]["ignite_ip"])+":"+str(config_file["gtp"]["tc_port"])+"/clearMessageBuffer",
"s1ap_buff_clr_url":"http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/clearMessageBuffer",
}

class ValidationException(Exception):
    def __init__(self,errorMessage):
        self.err_msg=errorMessage

def getFormattedDict(dic):
    formatted_obj = json.dumps(dic, indent=4, separators=(',', ': '))
    #print(formatted_obj)
    igniteLogger.logger.info("The formatted_obj : "f"{formatted_obj}")

def getKeyValueFromDict(dictToSearch, searchKey):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided. Returns the value for the searched key.
    """

    return_value = ""
    matched = "false"

    for key, value in dictToSearch.items():

        if key == searchKey:
            return_value = value
            matched = "true"
            break

        elif isinstance(value, dict):
            return_value_1, matched_1 = getKeyValueFromDict(value, searchKey)
            if matched_1 == "true":
                matched = matched_1
                return_value = return_value_1
                break

        elif isinstance(value, list):
            for i in range (len(value)):
                if isinstance(value[i], dict):
                    return_value_2, matched_2 =  getKeyValueFromDict(value[i], searchKey)
                    if matched_2 == "true":
                        matched = matched_2
                        return_value = return_value_2
                        break

    return return_value, matched

def updateKeyValueInDict(dictToUpdate, searchKey, newValue):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided. Once the key is found, update it with new value
    """
    updated_dict = dictToUpdate
    matched = "false"

    for key, value in dictToUpdate.items():

        if key == searchKey:
            matched = "true"
            dictToUpdate[key] = newValue
            break

        elif isinstance(value, dict):
            updatedDict_1, matched_1 = updateKeyValueInDict(value, searchKey, newValue)
            if matched_1 == "true":
                matched = matched_1
                value = updatedDict_1
                dictToUpdate[key] = value
                break

        elif isinstance(value, list):
            for i in range (len(value)):
                if isinstance(value[i], dict):
                    updatedDict_2, matched_2 = updateKeyValueInDict(value[i], searchKey, newValue)
                    if matched_2 == "true":
                        matched = matched_2
                        value[i] = updatedDict_2
                        dictToUpdate[key]= value
                        break

    updated_dict = dictToUpdate
    return updated_dict, matched

def convertBytesToIntArray(msgBytesObject):
    hex_str = msgBytesObject.decode('utf-8')
    int_list = [int(hex_str[i:i+2],16) for i in range(0,len(hex_str),2)]
    int_array = array('B', int_list)
    return int_array

def generateUniqueId(idType):
    if (idType == 'imsi'):
        start_value = 100000001
        end_value = 999999999
        url="http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/getContextData"
        response = requests.get(url)
        s1ap_ctx_data = response.json()
        while 1:
            rand_id = random.randint(start_value,end_value)
            unique_id = str(208920)+ str(rand_id)
            if s1ap_ctx_data !={} and unique_id in s1ap_ctx_data.keys():
                continue
            break
        unique_id = int(unique_id)
    elif idType == 'enbues1apid':
        start_value = 1
        end_value = 9999
        unique_id = random.randint(start_value,end_value)
    elif idType == 'gTP-TEID':
        start_value = 1
        end_value = 8
        id_value = random.randint(start_value,end_value)
        unique_id = convertToOctet(id_value)
    elif idType[:4] == 'guti':
        start_value = 1
        end_value = 9999
        rand_id = random.randint(start_value,end_value)
        if idType == 'guti_invalid':
            unique_id=[2, 0, 8, 9, 2, 15, 1, 2,rand_id]
        elif idType == 'guti_valid':
            unique_id=[2, 0, 8, 9, 2, 15, 1, 1,rand_id]

    return unique_id

def loadMessageData(messageFile):
	with open(messageFile) as data_file:
		msg_data = json.load(data_file)

	return msg_data["msgHeirarchy"], msg_data["msgDetails"]

def convertToOctet(value):
    octet = bin(value & int("1"*8, 2))[2:]
    return ("{0:0>%s}" % (8)).format(octet)

def icrementGtpTeid(value):
    val = (int(value,2))+1
    return convertToOctet(val)

def formatHex(value):
    return ("{0:0>%s}" % (8)).format(hex(value)[2:])

def validateProtocolIE(msg,validationParam,expectedValue):
    validation_param_value,validation_param_value_present=getKeyValueFromDict(msg,validationParam)
    if validation_param_value == expectedValue:
        igniteLogger.logger.info(f"EXTERNAL VALIDATION IEname:{validationParam} ,expected value:{expectedValue} ,received value:{validation_param_value}")
    else:
        igniteLogger.logger.error(f"EXTERNAL VALIDATION IEname:{validationParam} ,expected value:{expectedValue} ,received value:{validation_param_value}")
        raise ValidationException(f"EXTERNAL VALIDATION IEname:{validationParam} ,expected value:{expectedValue} ,received value:{validation_param_value}")
		
def clearBuffer():
    diameter_buff_clr_response = requests.get(url["diameter_buff_clr_url"])
    gtp_buff_clr_response = requests.get(url["gtp_buff_clr_url"])
    s1ap_buff_clr_response = requests.get(url["s1ap_buff_clr_url"])

def setValueFromTC(msg,ieUpdateValDict):
    for key in ieUpdateValDict.keys():
        updateKeyValueInDict(msg,key,ieUpdateValDict[key])
	


