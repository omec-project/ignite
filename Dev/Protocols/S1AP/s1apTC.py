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
import re
from s1apUtils import *
from s1apMsgUtils import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
import igniteCommonUtil as icu
from protocolMessageTypes import ProtocolMessageTypes as mt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'NAS', 'Util'))
import nasUtils as nu
import secUtils as su

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

configuration_file = os.path.join(os.path.dirname(__file__), '..','..','Common','configuration.json')
with open(configuration_file) as configuration:
                config_file=json.loads(configuration.read())

s1ap_validationtion_file = os.path.join(os.path.dirname(__file__),'s1apValidation.json')
with open(s1ap_validationtion_file) as s1ap_validation:
                s1ap_validation_file=json.loads(s1ap_validation.read())

nas_validationtion_file = os.path.join(os.path.dirname(__file__), '..', 'NAS', 'Util','nasValidation.json')
with open(nas_validationtion_file) as nas_validation:
                nas_validation_file=json.loads(nas_validation.read())



global IMSI
IMSI=None
global S1APCTXDATA
S1APCTXDATA={}
global SERFLAG
SERFLAG=False
global TIMEOUTFLAG
TIMEOUTFLAG=True
global GTP_TEID_LIST
GTP_TEID_LIST =[]

url={
"send_url":"http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/sendMessagesToProxy",
"receive_url":"http://"+str(config_file["s1ap"]["ignite_ip"])+":"+str(config_file["s1ap"]["tc_port"])+"/getMessagesfromProxy",
"diameter_ctx_data_url":"http://"+str(config_file["diameter"]["ignite_ip"])+":"+str(config_file["diameter"]["tc_port"])+"/getContextData",
"gtp_ctx_data_url":"http://"+str(config_file["gtp"]["ignite_ip"])+":"+str(config_file["gtp"]["tc_port"])+"/getContextData",
}

def receiveS1ap(ResponseWaitTime=10,target=None):
    global SERFLAG
    global TIMEOUTFLAG
    service="_service"
    time_out="_time_out"
    received_msg={}
    if target:
        url["receive_url"]= "http://" + str(config_file["s1ap_target"]["ignite_ip"]) + ":" + str(
            config_file["s1ap_target"]["tc_port"]) + "/getMessagesfromProxy"
    else:
        url["receive_url"]= "http://" + str(config_file["s1ap"]["ignite_ip"]) + ":" + str(
                            config_file["s1ap"]["tc_port"]) + "/getMessagesfromProxy"

    received_response =requests.get(url=url["receive_url"],timeout=ResponseWaitTime)
    igniteLogger.logger.info(f"URL response for receive s1ap data : {str(received_response)}")
    igniteLogger.logger.info(f"S1AP Data Received : {received_response.json()}")
    received_msg=received_response.json()
    procedure_code=s1apMessageDict[icu.getKeyValueFromDict(received_msg,'procedureCode')[0]]

    if procedure_code == mt.downlink_nas_transport.name:
        mobility_mgmt_message_type,mobility_mgmt_message_type_present=icu.getKeyValueFromDict(received_msg, "mobility_mgmt_message_type")
        if mobility_mgmt_message_type_present=='true':
            if mobility_mgmt_message_type in s1ApCreateContextMessagesList:
                setContextData(received_msg,mobility_mgmt_message_type)
            if SERFLAG:
                mobility_mgmt_message_type+=service
            validateS1apIE(mobility_mgmt_message_type,received_msg)
    else:
        if procedure_code == mt.initial_context_setup_request.name:
            if icu.getKeyValueFromDict(received_msg, "mobility_mgmt_message_type")[0]==mt.attach_accept.name:
                setContextData(received_msg,mt.attach_accept.name)

        elif procedure_code == mt.ue_context_release_command.name:
            setContextData(received_msg,procedure_code)

        if TIMEOUTFLAG:
            procedure_code+=time_out
        if SERFLAG:
            procedure_code+=service
        validateS1apIE(procedure_code,received_msg)

    return received_msg

def sendS1ap(requestType,s1apData,enbUeS1apId,nasData={},imsi=None,ieUpdateValDict=None):

    global SERFLAG
    global TIMEOUTFLAG
    global IMSI

    igniteLogger.logger.info(f"s1ap message type : {requestType}")
    s1apData["NAS-MESSAGE"] = nasData
    count=0
    
    if enbUeS1apId !=None:
        if requestType == mt.attach_request.name:
            icu.updateKeyValueInDict(s1apData, "ENB-UE-S1AP-ID", enbUeS1apId)
            nu.setImsi(imsi,nasData)
            if imsi ==None:
                S1APCTXDATA[enbUeS1apId]={}
            else:
                if S1APCTXDATA.get(IMSI,None)==None:
                    IMSI=imsi
                    S1APCTXDATA[IMSI]={}
                    S1APCTXDATA[IMSI][requestType]={'imsi':str(imsi)}

        elif requestType == mt.identity_response.name:
            IMSI=imsi
            nu.setImsi(imsi,nasData)
            if S1APCTXDATA.get(enbUeS1apId,None)!=None:
                S1APCTXDATA[IMSI]=S1APCTXDATA[enbUeS1apId].copy()
                del S1APCTXDATA[enbUeS1apId]
                S1APCTXDATA[IMSI][requestType]={'imsi':str(imsi)}
            updateMessageFromContextData(s1apData,requestType)
        elif requestType == mt.attach_request_guti.name:
            icu.updateKeyValueInDict(s1apData, "ENB-UE-S1AP-ID", enbUeS1apId)
            S1APCTXDATA[enbUeS1apId]={}
            if imsi!=None:
                nu.setGuti(imsi,s1apData)
            else:
                nu.setGuti(S1APCTXDATA[IMSI][mt.attach_accept.name]["guti_list"],s1apData)

        elif requestType==mt.service_request.name:
            SERFLAG=True
            icu.updateKeyValueInDict(s1apData, "ENB-UE-S1AP-ID", enbUeS1apId)
            icu.updateKeyValueInDict(s1apData,"m-TMSI", icu.formatHex(S1APCTXDATA[IMSI][mt.attach_accept.name]["m_tmsi"]))
            icu.updateKeyValueInDict(s1apData,"mMEC", '0'+str(S1APCTXDATA[IMSI][mt.attach_accept.name]["mme_code"]))
            updateMessageFromContextData(s1apData,requestType)

        else:
            if requestType == mt.initial_context_setup_response.name:
                if count == 0:
                    gtp_teid=icu.generateUniqueId('gTP-TEID')
                    S1APCTXDATA[IMSI]["gTP_TEID"]=gtp_teid
                    icu.updateKeyValueInDict(s1apData, "gTP-TEID", gtp_teid)
                    count+=1
                else:
                    gtp_teid=S1APCTXDATA[IMSI]["gTP_TEID"]
                    gtp_teid=icu.icrementGtpTeid(gtp_teid)
                    S1APCTXDATA[IMSI]["gTP_TEID"]=gtp_teid
                    icu.updateKeyValueInDict(s1apData, "gTP-TEID", gtp_teid)
                    count+=1
                icu.updateKeyValueInDict(s1apData, "transportLayerAddress",transportLayerAddressUpdate())

            elif requestType == mt.handover_request_acknowledge.name:
                gtp_teid=icu.generateUniqueId('gTP-TEID')
                gtp_teid_1=icu.generateUniqueId('gTP-TEID')
                S1APCTXDATA[IMSI]["gTP_TEID_2"]=gtp_teid
                icu.updateKeyValueInDict(s1apData, "gTP-TEID", gtp_teid)
                icu.updateKeyValueInDict(s1apData, "transportLayerAddress",transportLayerAddressUpdate())
                icu.updateKeyValueInDict(s1apData, "dL-transportLayerAddress",transportLayerAddressUpdate())
                icu.updateKeyValueInDict(s1apData, "gTP-TEID", gtp_teid_1)

            elif requestType == mt.erab_modification_indication.name:
                tl_address=transportLayerAddressUpdate()
                generateIeValueForErabModInd(s1apData,tl_address,GTP_TEID_LIST)
                S1APCTXDATA[IMSI]["gTP_TEID"]=GTP_TEID_LIST
            
            elif requestType==mt.authentication_response.name:
                TIMEOUTFLAG=False

            elif requestType==mt.ue_context_release_complete.name:
                SERFLAG=False

            updateMessageFromContextData(s1apData,requestType)

    if ieUpdateValDict != None:
        icu.setValueFromTC(s1apData,ieUpdateValDict)
    setContextData(s1apData,requestType)

    igniteLogger.logger.info(f"s1ap data send : {s1apData}")
    if requestType in [mt.s1_setup_request_target.name,mt.handover_request_acknowledge.name,mt.handover_notify.name]:
        send_url = "http://"+str(config_file["s1ap_target"]["ignite_ip"])+":"+str(config_file["s1ap_target"]["tc_port"])+"/sendMessagesToProxy"
        send_response = requests.post(url["send_url"], json=[None,S1APCTXDATA,"s1ap"])
    else:
        send_url = url["send_url"]
    
    send_response = requests.post(send_url, json=[s1apData, S1APCTXDATA, "s1ap", IMSI])
    
    igniteLogger.logger.info(f"URL response for send s1ap data : {str(send_response)}")

def setContextData(s1apMsg,requestType):
    global IMSI
    enb_ue_s1ap_id, enb_ue_s1ap_id_present = icu.getKeyValueFromDict(s1apMsg, "ENB-UE-S1AP-ID")

    if requestType==mt.attach_request.name or requestType==mt.attach_request_guti.name:
        if S1APCTXDATA.get(enb_ue_s1ap_id,None)==None:
            key = IMSI
        else:
            key = enb_ue_s1ap_id
        plmn_identity, plmn_identity_present = icu.getKeyValueFromDict(s1apMsg, "pLMNidentity")
        nas_ksi_attach, nas_ksi_attach_present = icu.getKeyValueFromDict(s1apMsg, "nas_key_set_identifier")
        if S1APCTXDATA[key].get(mt.attach_request.name,None)==None:
            S1APCTXDATA[key][mt.attach_request.name]={"enb_ue_s1ap_id":enb_ue_s1ap_id}
        else:
            S1APCTXDATA[key][mt.attach_request.name]["enb_ue_s1ap_id"]=enb_ue_s1ap_id
        S1APCTXDATA[key][mt.attach_request.name]["plmn_identity"] = plmn_identity
        S1APCTXDATA[key][mt.attach_request.name]["nas_key_set_identifier"] = nas_ksi_attach

    elif requestType==mt.authentication_request.name:
        mme_ue_s1ap_id, mme_ue_s1ap_id_present = icu.getKeyValueFromDict(s1apMsg, "MME-UE-S1AP-ID")
        S1APCTXDATA[IMSI][requestType]={"mme_ue_s1ap_id":mme_ue_s1ap_id}
        nas_ksi, nas_ksi_present = icu.getKeyValueFromDict(s1apMsg, "nas_key_set_identifier_auth_req")
        response = requests.get(url["diameter_ctx_data_url"])
        imsiKey = str(IMSI)
        if response.json() != {} and response.json().get(imsiKey, None) != None:
            S1APCTXDATA[IMSI]['SEC_CXT'] = {}
            S1APCTXDATA[IMSI]['SEC_CXT']['KSI'] = nas_ksi
            #TODO: Fetch KASME based on KSI
            S1APCTXDATA[IMSI]['SEC_CXT']['KASME'] = response.json()[imsiKey]["authentication_info_response"]["kasme"]
            S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT'] = 0
            #TODO: Support DL NAS Count && MAC validation
            
    elif requestType==mt.security_mode_command.name:
        # MME is trying to establish/re-establish 
        # integrity protection. Reset counts to 0 
        S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT'] = 0

    elif  requestType==mt.identity_request.name:
        mme_ue_s1ap_id, mme_ue_s1ap_id_present = icu.getKeyValueFromDict(s1apMsg, "MME-UE-S1AP-ID")
        S1APCTXDATA[enb_ue_s1ap_id][requestType]={"mme_ue_s1ap_id":mme_ue_s1ap_id}

    elif requestType==mt.attach_accept.name:
        guti_list=nu.getGuti(s1apMsg)
        m_tmsi, m_tmsi_present = icu.getKeyValueFromDict(s1apMsg, "m_tmsi")
        mme_code, mme_code_present = icu.getKeyValueFromDict(s1apMsg, "mme_code")
        tai_list, tai_list_present = icu.getKeyValueFromDict(s1apMsg,"tracking_area_identity_list")
        selected_tai = taiEcgiTohex(tai_list)
        S1APCTXDATA[IMSI][requestType]={"guti_list":guti_list,"m_tmsi":m_tmsi,"mme_code":mme_code,"tai_dict":selected_tai}

    elif requestType == mt.initial_context_setup_response.name:
        transport_layer_address,transport_layer_address_present = icu.getKeyValueFromDict(s1apMsg,"transportLayerAddress")
        gtp_teid,gtp_teid_present = icu.getKeyValueFromDict(s1apMsg,"gTP-TEID")
        S1APCTXDATA[IMSI][requestType]={"transport_layer_address":transport_layer_address,"gtp_teid":int(gtp_teid,16)}

    elif requestType == mt.handover_request_acknowledge.name:
        transport_layer_address,transport_layer_address_present = icu.getKeyValueFromDict(s1apMsg,"transportLayerAddress")
        gtp_teid,gtp_teid_present = icu.getKeyValueFromDict(s1apMsg,"gTP-TEID")
        S1APCTXDATA[IMSI][mt.initial_context_setup_response.name]={"transport_layer_address":transport_layer_address,"gtp_teid":int(gtp_teid,16)}

    elif requestType == mt.erab_modification_indication.name:
        transport_layer_address,transport_layer_address_present = icu.getKeyValueFromDict(s1apMsg,"transportLayerAddress")
        gtp_teid, gtp_teid_present = icu.getKeyValueFromDict(s1apMsg, "dL-GTP-TEID")
        S1APCTXDATA[IMSI][mt.initial_context_setup_response.name] = {"transport_layer_address": transport_layer_address,"gtp_teid": int(gtp_teid, 16)}
    
    elif requestType==mt.service_request.name:
        S1APCTXDATA[IMSI][requestType]={"enb_ue_s1ap_id":enb_ue_s1ap_id}

    elif requestType == mt.ue_context_release_command.name:
        mme_ue_s1ap_id, mme_ue_s1ap_id_present = icu.getKeyValueFromDict(s1apMsg, "mME-UE-S1AP-ID")
        if IMSI == None:
            S1APCTXDATA[enb_ue_s1ap_id][requestType]={"mme_ue_s1ap_id":mme_ue_s1ap_id}
        else:
            S1APCTXDATA[IMSI][requestType]={"mme_ue_s1ap_id":mme_ue_s1ap_id}

    elif requestType == mt.esm_information_response.name:
        apn , apn_present = icu.getKeyValueFromDict(s1apMsg, "apn_esm")
        S1APCTXDATA[IMSI][requestType]={"apn":apn}
        
    elif requestType == mt.securitymode_complete.name:
        S1APCTXDATA[IMSI]['SEC_CXT']['INTEGRITY_KEY'] = su.createIntegrityKey(2, str(S1APCTXDATA[IMSI]["SEC_CXT"]["KASME"]))

    procedure_code, matched = icu.getKeyValueFromDict(s1apMsg,'procedureCode')
    if matched and procedure_code == 13: #uplink nas
        if  s1apMsg.get('NAS-MESSAGE', None) != None and 'sequence_number' in s1apMsg['NAS-MESSAGE'].keys():
            S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT'] += 1
    elif matched and procedure_code == 12: #Init ue -service request
        if  s1apMsg.get('NAS-MESSAGE', None) != None and 'ksi_sequence_number' in s1apMsg['NAS-MESSAGE'].keys():
            S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT'] += 1
        
    igniteLogger.logger.info(f"s1ap context data : {S1APCTXDATA}")


def updateMessageFromContextData(s1apMsg,requestType):
    global IMSI

    if requestType==mt.detach_request.name:
        nu.setGuti(S1APCTXDATA[IMSI][mt.attach_accept.name]["guti_list"],s1apMsg)

    elif requestType==mt.tau_request.name:
        nu.setGuti(S1APCTXDATA[IMSI][mt.attach_accept.name]["guti_list"],s1apMsg)

    elif requestType==mt.handover_required.name:
        icu.updateKeyValueInDict(s1apMsg, "selected-TAI", S1APCTXDATA[IMSI][mt.attach_accept.name]["tai_dict"])

    if S1APCTXDATA[IMSI].get(mt.service_request.name,None)!=None:
        icu.updateKeyValueInDict(s1apMsg, "ENB-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.service_request.name]["enb_ue_s1ap_id"])
    else:
        icu.updateKeyValueInDict(s1apMsg, "ENB-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.attach_request.name]["enb_ue_s1ap_id"])

    if S1APCTXDATA[IMSI].get(mt.initial_context_setup_request.name,None)!=None:
        icu.updateKeyValueInDict(s1apMsg, "MME-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.initial_context_setup_request.name]["mme_ue_s1ap_id"])
    elif S1APCTXDATA[IMSI].get(mt.identity_request.name,None)!=None:
        icu.updateKeyValueInDict(s1apMsg, "MME-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.identity_request.name]["mme_ue_s1ap_id"])
    elif S1APCTXDATA[IMSI].get(mt.authentication_request.name,None)!=None:
        icu.updateKeyValueInDict(s1apMsg, "MME-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.authentication_request.name]["mme_ue_s1ap_id"])
    elif S1APCTXDATA[IMSI].get(mt.ue_context_release_command.name,None)!=None:
        icu.updateKeyValueInDict(s1apMsg, "MME-UE-S1AP-ID", S1APCTXDATA[IMSI][mt.ue_context_release_command.name]["mme_ue_s1ap_id"])

    updateMessageFromSecurityContext(s1apMsg, requestType)
    
def updateMessageFromSecurityContext(s1apMsg,requestType):
    global IMSI

    procedure_code, matched = icu.getKeyValueFromDict(s1apMsg, 'procedureCode')
    if matched and procedure_code == 13:  # uplink nas
        if s1apMsg.get('NAS-MESSAGE', None) != None:
            if 'message_authentication_code' in s1apMsg['NAS-MESSAGE'].keys():
                s1apMsg['NAS-MESSAGE']['message_authentication_code'] = 0
            if 'sequence_number' in s1apMsg['NAS-MESSAGE'].keys():
                s1apMsg['NAS-MESSAGE']['sequence_number'] = S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT']
            if 'nas_key_set_identifier_detach_request' in s1apMsg['NAS-MESSAGE'].keys():
                if 'nas_key_set_identifier_detach_request_value' in s1apMsg['NAS-MESSAGE']['nas_key_set_identifier_detach_request'].keys():
                   s1apMsg['NAS-MESSAGE']['nas_key_set_identifier_detach_request']['nas_key_set_identifier_detach_request_value'] = S1APCTXDATA[IMSI]['SEC_CXT']['KSI']

    elif matched and procedure_code == 12:  #Init ue - service req
        if s1apMsg.get('NAS-MESSAGE', None) != None:
            if 'message_authentication_code_short' in s1apMsg['NAS-MESSAGE'].keys():
                s1apMsg['NAS-MESSAGE']['message_authentication_code_short'] = 0
            if 'ksi_sequence_number' in s1apMsg['NAS-MESSAGE'].keys():
                if 'nas_key_set_identifier_service_req' in s1apMsg['NAS-MESSAGE']['ksi_sequence_number'].keys():
                    s1apMsg['NAS-MESSAGE']['ksi_sequence_number']['nas_key_set_identifier_service_req'] = S1APCTXDATA[IMSI]['SEC_CXT']['KSI']
                if 'sequence_number_service_req' in s1apMsg['NAS-MESSAGE']['ksi_sequence_number'].keys():
                    s1apMsg['NAS-MESSAGE']['ksi_sequence_number']['sequence_number_service_req'] = S1APCTXDATA[IMSI]['SEC_CXT']['UPLINK_COUNT']

    if requestType == mt.tau_request.name:
        icu.updateKeyValueInDict(s1apMsg, "nas_key_set_identifier", S1APCTXDATA[IMSI][mt.attach_request.name]['nas_key_set_identifier'])

def validateS1apIE(requestType,s1apMsg):
    global SERFLAG
    global IMSI

    procedure_code=s1apMessageDict[icu.getKeyValueFromDict(s1apMsg,'procedureCode')[0]]
    if procedure_code == mt.downlink_nas_transport.name:
        validation_dict=nas_validation_file.get(requestType,None)
    else:
        validation_dict=s1ap_validation_file.get(requestType,None)

    if validation_dict !=None:
        response = requests.get(url["diameter_ctx_data_url"])
        if response.json() !={} and response.json().get(str(IMSI),None)!=None:
            diameter_data = response.json()[str(IMSI)]

        response = requests.get(url["gtp_ctx_data_url"])
        if response.json() !={} and response.json().get(str(IMSI),None)!=None:
            gtp_data = response.json()[str(IMSI)]

        for num in range(len(validation_dict["dataToBeVerified"])):
            val_flag=False
            ie_to_validate=validation_dict["dataToBeVerified"][num]
            data_to_compare_path=validation_dict["fromContextData"][num].split(':')

            ie_to_validate_value,ie_to_validate_value_present=icu.getKeyValueFromDict(s1apMsg,ie_to_validate)

            if data_to_compare_path[0] == "s1apContextData":
                if requestType == mt.identity_request.name:
                    data_to_compare=S1APCTXDATA[icu.getKeyValueFromDict(s1apMsg,"ENB-UE-S1AP-ID")[0]]
                else:
                    data_to_compare=S1APCTXDATA[IMSI]
            elif data_to_compare_path[0] == "diameterContextData":
                data_to_compare = diameter_data

            elif data_to_compare_path[0] == "gtpContextData":
                data_to_compare = gtp_data

            data_to_compare_value,data_to_compare_value_present=icu.getKeyValueFromDict(data_to_compare[data_to_compare_path[1]],data_to_compare_path[2])

            if ie_to_validate == "transportLayerAddress":
                data_to_compare_value=convertIpaddressToHex(data_to_compare_value)
            elif ie_to_validate == "m-TMSI":
                data_to_compare_value=icu.formatHex(data_to_compare_value)

            if ie_to_validate_value == data_to_compare_value:
                val_flag = True
            elif type(ie_to_validate_value)==str and data_to_compare_value in ie_to_validate_value:
                val_flag = True

            if val_flag:
                igniteLogger.logger.info(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
            else:
                igniteLogger.logger.error(f"request/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}")
                raise icu.ValidationException(f"***** ***** *****\nERROR :: Validation fail \nrequest/response name:{requestType} ,IEname:{ie_to_validate} ,expected value:{data_to_compare_value} ,received value:{ie_to_validate_value}***** ***** *****")



