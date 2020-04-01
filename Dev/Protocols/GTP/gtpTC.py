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


from binascii import hexlify
import json
import os
import sys
import requests
import time
from gtpUtils import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
import igniteCommonUtil as icu
from protocolMessageTypes import ProtocolMessageTypes as mt

validationtion_file = os.path.join(os.path.dirname(__file__),'gtpValidation.json')
with open(validationtion_file) as validation:
                validation_file=json.loads(validation.read())


configuration_file = os.path.join(os.path.dirname(__file__), '..','..','Common','configuration.json')
with open(configuration_file) as configuration:
        config_file=json.loads(configuration.read())


global S11CTXDATA
S11CTXDATA={}

global IMSI
IMSI=None

url={
"send_url":"http://"+str(config_file["gtp"]["ignite_ip"])+":"+str(config_file["gtp"]["tc_port"])+"/sendMessagesToProxy",
"receive_url":"http://"+str(config_file["gtp"]["ignite_ip"])+":"+str(config_file["gtp"]["tc_port"])+"/getMessagesfromProxy",
"s1ap_ctx_data_url":"http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/getContextData",
"diameter_ctx_data_url":"http://"+str(config_file["diameter"]["ignite_ip"])+":"+str(config_file["diameter"]["tc_port"])+"/getContextData",
}

def receiveGtp(ResponseWaitTime=10):
    global IMSI
    received_msg={}
    receive_response = requests.get(url=url["receive_url"],timeout=ResponseWaitTime)
    igniteLogger.logger.info(f"URL response for receive gtp data  : {str(receive_response)}")
    igniteLogger.logger.info(f"Gtp data received : {receive_response.json()}")
    received_msg= receive_response.json()
    message_type, message_type_present = icu.getKeyValueFromDict(received_msg, "message_type")
    if gtpMessageDict[message_type] == mt.create_session_request.name:
        IMSI =icu.getKeyValueFromDict(received_msg,"imsi")[0]
    validateGtpIE(gtpMessageDict[message_type], received_msg)
    setContextData(gtpMessageDict[message_type],received_msg)
    return received_msg


def sendGtp(requestType, msgData, msgHeirarchy, ieUpdateValDict=None):
    igniteLogger.logger.info(f"Gtp Message type : {requestType}")
    updateMessageFromContextData(requestType, msgData)
    if ieUpdateValDict != None:
        icu.setValueFromTC(msgData,ieUpdateValDict)
    if requestType == mt.create_session_response.name:
        setContextData(requestType,msgData)
    igniteLogger.logger.info(f"Gtp data received : {msgData}")
    send_response = requests.post(url=url["send_url"], json=[msgData,S11CTXDATA,"gtp"])
    igniteLogger.logger.info(f"URL response for send gtp data  : {str(send_response)}")


def setContextData(requestType,gtpMsg):
    global IMSI

    if requestType == mt.create_session_response.name:
       teid_gre_key,teid_gre_key_present = icu.getKeyValueFromDict(gtpMsg, "teid_gre_key")
       ipv4_address,ipv4_address_present = icu.getKeyValueFromDict(gtpMsg, "ipv4address")
       eps_bearer_id,eps_bearer_id_present = icu.getKeyValueFromDict(gtpMsg, "eps_bearer_id")
       S11CTXDATA[IMSI][requestType]={"teid_gre_key":icu.formatHex(teid_gre_key),"ipv4_address":ipv4_address,"eps_bearer_id":eps_bearer_id}

    else:
        seq_number, seq_number_present = icu.getKeyValueFromDict(gtpMsg, "sequence_number")
        mme_teid, mme_teid_present = icu.getKeyValueFromDict(gtpMsg, "teid_gre_key")

        if requestType == mt.create_session_request.name:
            if S11CTXDATA.get(IMSI,None) ==None:
                S11CTXDATA[IMSI]={}

        if mme_teid_present =='true':
            S11CTXDATA[IMSI][requestType]={"sequence_number":seq_number,"teid_key":mme_teid}
        else:
            S11CTXDATA[IMSI][requestType]={"sequence_number":seq_number}
    igniteLogger.logger.info(f"GTP context data  : {S11CTXDATA}")

def updateMessageFromContextData(requestType, gtpMsg):
    global IMSI
    seq_count=0

    message_type, message_type_present = icu.getKeyValueFromDict(gtpMsg, "message_type")
	
    if gtpMessageDict[message_type] in gtpInitialMessagesList:
        seq_count+=1
        icu.updateKeyValueInDict(gtpMsg, "sequence_number",seq_count)
    else:
        message_type=gtpRespReqDict[requestType]
        icu.updateKeyValueInDict(gtpMsg, "sequence_number",S11CTXDATA[IMSI][message_type]["sequence_number"])
    icu.updateKeyValueInDict(gtpMsg, "teid",S11CTXDATA[IMSI][mt.create_session_request.name]["teid_key"])

def validateGtpIE(requestType,gtpMsg):
    global SEQNUM
    global IMSI

    response = requests.get(url["s1ap_ctx_data_url"])
    s1ap_data = response.json()
    if response.json() !={} and response.json().get(IMSI,None)!=None:
        s1ap_data = s1ap_data[IMSI]

    response = requests.get(url["diameter_ctx_data_url"])
    if response.json() !={} and response.json().get(IMSI,None)!=None:
        diameter_data = response.json()[IMSI]

    validation_dict=validation_file.get(requestType,None)
    if validation_dict !=None:
        for num in range(len(validation_dict["dataToBeVerified"])):
            val_flag=False
            ie_to_validate=validation_dict["dataToBeVerified"][num]
            data_to_compare_path=validation_dict["fromContextData"][num].split(':')
            if ie_to_validate == "tai" or ie_to_validate=="ecgi":
                ie_to_validate_value=taiEcgiTohex(icu.getKeyValueFromDict(gtpMsg,ie_to_validate)[0])
            elif ie_to_validate == "ipv4address":
                ie_to_validate_value=ipadressToHex(icu.getKeyValueFromDict(gtpMsg,ie_to_validate)[0])
            else:
                ie_to_validate_value,ie_to_validate_value_present=icu.getKeyValueFromDict(gtpMsg,ie_to_validate)

            if ie_to_validate == "rat_type":
                val_flag,data_to_compare_value = validateRatType(ie_to_validate_value)
            elif ie_to_validate == "interface_type":
                val_flag,data_to_compare_value = validateInterfaceType(ie_to_validate_value)
            else:
                if data_to_compare_path[0] == "gtpContextData":
                    data_to_compare=S11CTXDATA[IMSI]

                elif data_to_compare_path[0] == "s1apContextData":
                    data_to_compare=s1ap_data

                elif data_to_compare_path[0] == "diameterContextData":
                    data_to_compare=diameter_data 

                data_to_compare_value,data_to_compare_value_present=icu.getKeyValueFromDict(data_to_compare[data_to_compare_path[1]],data_to_compare_path[2])

                if data_to_compare_value_present == "false":
                    if ie_to_validate =="imsi":
                        data_to_compare_value,data_to_compare_value_present=icu.getKeyValueFromDict(data_to_compare[mt.identity_response.name],data_to_compare_path[2])

            if ie_to_validate_value == data_to_compare_value:
                val_flag=True

            if val_flag:
                igniteLogger.logger.info(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
            else:
                igniteLogger.logger.error(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
                raise icu.ValidationException(f"***** ***** *****\nERROR :: Validation fail \nrequest/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}***** ***** *****")

def validateRatType(value):
    if value == rat_type_gtp_map["EUTRAN"]:
        return True,rat_type_gtp_map["EUTRAN"]
    return False,rat_type_gtp_map["EUTRAN"]

def validateInterfaceType(value):
    if value == interface_type_gtp_map["S11 MME GTP-C"]:
        return True,interface_type_gtp_map["S11 MME GTP-C"]
    return False,interface_type_gtp_map["S11 MME GTP-C"]

