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
import os
import sys
import json
import requests
import time
from diameterUtils import *


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from protocolMessageTypes import ProtocolMessageTypes as mt
import igniteCommonUtil as icu

validation_file = os.path.join(os.path.dirname(__file__),'diameterValidation.json')
with open(validation_file) as validation:
                validation_file=json.loads(validation.read())


configuration_file = os.path.join(os.path.dirname(__file__), '..','..', 'Common','configuration.json')
with open(configuration_file) as configuration:
        config_file=json.loads(configuration.read())

S6ACTXDATA={}
global IMSI
IMSI=None

url={
"send_url":"http://"+str(config_file["diameter"]["ignite_ip"])+":"+str(config_file["diameter"]["tc_port"])+"/sendMessagesToProxy",
"receive_url":"http://"+str(config_file["diameter"]["ignite_ip"])+":"+str(config_file["diameter"]["tc_port"])+"/getMessagesfromProxy",
"s1ap_ctx_data_url":"http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/getContextData",
"gtp_ctx_data_url":"http://"+str(config_file["gtp"]["ignite_ip"])+":"+str(config_file["gtp"]["tc_port"])+"/getContextData"
}


def receiveS6aMsg(responseWaitTime=10):
    received_msg={}
    receive_response = requests.get(url=url["receive_url"],timeout=responseWaitTime)
    igniteLogger.logger.info(f"URL response for receive diameter data: {str(receive_response)}")
    igniteLogger.logger.info(f"diameter data : {receive_response.json()}")
    received_msg=receive_response.json()
    command_code = get(received_msg,"diameter","command-code")
    setContextData(diameterMessageDict[command_code], received_msg)
    validateDiameterAvp(diameterMessageDict[command_code], received_msg)
    igniteLogger.logger.info(f"diameter Context data : {S6ACTXDATA}")
    return received_msg


def sendS6aMsg(requestType,msgData,userName,ieUpdateValDict=None):
    global IMSI
    
    igniteLogger.logger.info(f"Diameter message Type : {requestType}")
    if requestType == mt.update_location_response.name:
        response = requests.get(url["s1ap_ctx_data_url"])
        if response.json()!={} and response.json().get(IMSI,None)!=None:
            s1ap_data = response.json()[IMSI]
            icu.updateKeyValueInDict(msgData,"service-selection",s1ap_data[mt.esm_information_response.name]["apn"]) 
    updateMessageFromContextData(requestType,msgData)
    if ieUpdateValDict != None:
        icu.setValueFromTC(msgData,ieUpdateValDict)
    setContextData(requestType,msgData)
    igniteLogger.logger.info(f"Data to be sent : {msgData}")
    send_response = requests.post(url=url["send_url"], json=[msgData,S6ACTXDATA,"diameter"])
    igniteLogger.logger.info(f"URL response for send diameter data: {str(send_response)}")
	
def setContextData(requestType, diameterMsg):
    global S6ACTXDATA
    global IMSI

    session_id = get(diameterMsg,"diameter","session-id")
    hbh = get(diameterMsg,"diameter","hop-by-hop-identifier")
    ete = get(diameterMsg,"diameter","end-to-end-identifier")
    user_name = get(diameterMsg,"diameter","user-name")
    if user_name != None:
        IMSI=user_name
        if S6ACTXDATA.get(IMSI,None)==None:
            S6ACTXDATA[user_name]={}
        
    if requestType == mt.authentication_info_response.name:
        autn,autn_present = icu.getKeyValueFromDict(diameterMsg,"autn")
        rand,rand_present = icu.getKeyValueFromDict(diameterMsg,"rand")
        kasme, kasme_present = icu.getKeyValueFromDict(diameterMsg,"kasme")
        S6ACTXDATA[IMSI][requestType]={"autn":int(autn,16),"rand":int(rand,16), "kasme":kasme}
            
    elif requestType == mt.update_location_response.name:
        msisdn,msisdn_present = icu.getKeyValueFromDict(diameterMsg,"msisdn")
        S6ACTXDATA[IMSI][requestType]={"msisdn":msisdn}
    elif requestType == mt.cancel_location_request.name:
        destination_host,destination_host_present = icu.getKeyValueFromDict(diameterMsg,"destination-host")
        destination_realm,destination_realm_present = icu.getKeyValueFromDict(diameterMsg,"destination-realm")
        S6ACTXDATA[IMSI][requestType]={"destination_host":destination_host,"destination_realm":destination_realm,"session_id":session_id}
    else:
        S6ACTXDATA[IMSI][requestType]={"user_name":user_name,"session_id":session_id,"hop_by_hop_identifier":hbh,"end_to_end_identifier":ete}



def updateMessageFromContextData(requestType,diameterMsg):
    global S6ACTXDATA
    global IMSI
    
    if icu.getKeyValueFromDict(diameterMsg,"origin-host")[1]=="true":
        replace(diameterMsg,"diameter","origin-host",config_file["diameter"]["ignite_host"])
    if icu.getKeyValueFromDict(diameterMsg,"origin-realm")[1]=="true":
                replace(diameterMsg,"diameter","origin-realm",config_file["diameter"]["ignite_realm"])
    if icu.getKeyValueFromDict(diameterMsg,"destination-host")[1]=="true":
                replace(diameterMsg,"diameter","destination-host",config_file["diameter"]["mme_host"])
    if icu.getKeyValueFromDict(diameterMsg,"destination-realm")[1]=="true":
                replace(diameterMsg,"diameter","destination-realm",config_file["diameter"]["mme_realm"])


    if requestType == mt.cancel_location_request.name:
        diameterMsg = replace(diameterMsg,"diameter","user-name",S6ACTXDATA[IMSI][diameterRespReqDict[mt.update_location_response.name]]["user_name"])
    else:
        diameterMsg = replace(diameterMsg,"diameter","session-id",S6ACTXDATA[IMSI][diameterRespReqDict[requestType]]["session_id"])
        diameterMsg = replace(diameterMsg,"diameter","hop-by-hop-identifier",S6ACTXDATA[IMSI][diameterRespReqDict[requestType]]["hop_by_hop_identifier"])
        diameterMsg = replace(diameterMsg,"diameter","end-to-end-identifier",S6ACTXDATA[IMSI][diameterRespReqDict[requestType]]["end_to_end_identifier"])


def validateDiameterAvp(requestType,diameterMsg):
    global IMSI
    validation_dict=validation_file.get(requestType,None)

    response = requests.get(url["s1ap_ctx_data_url"])
    if response.json()!={} and response.json().get(IMSI,None)!=None:
        s1ap_data = response.json()[IMSI]

    response = requests.get(url["gtp_ctx_data_url"])
    if response.json() !={} and response.json().get(IMSI,None)!=None:
        gtp_data = response.json()[IMSI]

    if validation_dict !=None:
        for num in range(len(validation_dict["dataToBeVerified"])):
            val_flag=False
            ie_to_validate=validation_dict["dataToBeVerified"][num] 
            data_to_compare_path=validation_dict["fromContextData"][num].split(":") #collecting the path of expected data for AVP
            ie_to_validate_value,ie_to_validate_value_present=icu.getKeyValueFromDict(diameterMsg,ie_to_validate)
            if ie_to_validate == "rat-type":
                if ie_to_validate_value == rat_type_diameter_map["EUTRAN"]:
                    val_flag = True
            else:

                if data_to_compare_path[0] == "diameterContextData":
                    data_to_compare=S6ACTXDATA[IMSI]

                elif data_to_compare_path[0] == "s1apContextData":
                    data_to_compare = s1ap_data

                elif data_to_compare_path[0] == "gtpContextData":
                    data_to_compare = gtp_data

                data_to_compare_value,data_to_compare_value_present=icu.getKeyValueFromDict(data_to_compare[data_to_compare_path[1]],data_to_compare_path[2])

                if data_to_compare_value_present == "false":
                    if ie_to_validate =="user-name":
                        data_to_compare_value,data_to_compare_value_present=icu.getKeyValueFromDict(data_to_compare[mt.identity_response.name],data_to_compare_path[2])

                if ie_to_validate_value == data_to_compare_value:
                    val_flag=True

            if val_flag == True:
                igniteLogger.logger.info(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
            else:
                igniteLogger.logger.error(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
                raise icu.ValidationException(f"***** ***** *****\nERROR :: Validation fail \nrequest/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}***** ***** *****")

