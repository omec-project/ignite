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
import sys, requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Dev', 'Common'))
import igniteCommonUtil as icu
import sshUtils as su

sys.path.append(os.path.join(os.path.dirname(__file__), '..','ROBOTCs','keywords','systemkeywords'))
import dictOperations as do

clr_flag=False
ssh_client = None

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MessageTemplates', 'Util'))
    from loadMessage import *

    command = "export LD_LIBRARY_PATH=" + mme_lib_path + " && " + mme_grpc_client_path + "/mme-grpc-client mme-app show procedure-stats"

    ssh_client = su.sshConnect(mmeIP, mme_username, mme_password, "ssh-password", timeout=10, port=None)
    proc_stat = su.executeCommand(command,ssh_client)

    ue_count_before_attach = int(do.splitProcStats(proc_stat, stats_type["subs_attached"]))
    num_of_erab_mod_indication = int(do.splitProcStats(proc_stat, stats_type["erab_mod_ind"]))
    num_of_erab_mod_confirmation = int(do.splitProcStats(proc_stat, stats_type["erab_mod_conf"]))

    #required message templates
    uplinknastransport_detach_accept = json.loads(open('../MessageTemplates/S1AP/uplinknastransport_detachaccept.json').read())
    nas_detach_accept = json.loads(open('../MessageTemplates/NAS/detach_accept.json').read())
    

    print ("\n-------------------------------------\nIMSI Attach eRAB Mod Ind MB Resp Failure Execution Started\n---------------------------------------")

    igniteLogger.logger.info("\n---------------------------------------\nSend Attach Request to MME\n---------------------------------------")
    s1.sendS1ap('attach_request',initial_ue,enbues1ap_id,nas_attach_request,imsi)


    igniteLogger.logger.info("\n---------------------------------------\nHSS receives AIR from MME\n---------------------------------------")
    air=ds.receiveS6aMsg()
    icu.validateProtocolIE(air,'visited-plmn-id','02f829')

    igniteLogger.logger.info("\n---------------------------------------\nHSS sends AIA to MME\n---------------------------------------")
    ds.sendS6aMsg('authentication_info_response', msg_data_aia, imsi)

    igniteLogger.logger.info(
            "\n---------------------------------------\nAuth Request received from MME\n---------------------------------------")
    auth_req=s1.receiveS1ap()
    icu.validateProtocolIE(auth_req,'mobility_mgmt_message_type','authentication_request')

    igniteLogger.logger.info("\n---------------------------------------\nSend Auth Response to MME\n---------------------------------------")
    s1.sendS1ap('authentication_response', uplinknastransport_auth_response, enbues1ap_id, nas_authentication_response)

    igniteLogger.logger.info("\n---------------------------------------\nSecurity Mode Command received from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nSend Security Mode Complete to MME\n---------------------------------------")
    s1.sendS1ap('securitymode_complete', uplinknastransport_securitymode_complete, enbues1ap_id, nas_securitymode_complete)

    igniteLogger.logger.info("\n---------------------------------------\nESM Information Request from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nESM Information Response to MME\n---------------------------------------")
    s1.sendS1ap('esm_information_response', uplinknastransport_esm_information_response, enbues1ap_id, nas_esm_information_response)

    igniteLogger.logger.info("\n---------------------------------------\nHSS receives ULR from MME\n---------------------------------------")
    ulr=ds.receiveS6aMsg()
    hop_to_hop_identifier=icu.getKeyValueFromDict(ulr,"hop-by-hop-identifier")[0]

    igniteLogger.logger.info("\n---------------------------------------\nHSS sends ULA to MME\n---------------------------------------")
    icu.updateKeyValueInDict(msg_data_ula,"hop-by-hop-identifier",hop_to_hop_identifier)
    ds.sendS6aMsg('update_location_response', msg_data_ula, imsi)

    clr_flag=True

    igniteLogger.logger.info("\n---------------------------------------\nCreate Session Request received from MME\n---------------------------------------")
    cs_req=gs.receiveGtp()
    icu.validateProtocolIE(cs_req,'apn','apn1')
    icu.validateProtocolIE(cs_req,'pdn_type',1)

    igniteLogger.logger.info("\n---------------------------------------\nSend Create Session Response to MME\n---------------------------------------")
    gs.sendGtp('create_session_response', create_session_response, msg_hierarchy)

    igniteLogger.logger.info("\n---------------------------------------\nInitial Context Setup Request received from MME\n---------------------------------------")
    init_ctxt_setup_req=s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nSend Initial Context Setup Response to MME\n---------------------------------------")
    s1.sendS1ap('initial_context_setup_response', initialcontextsetup_response, enbues1ap_id)

    time.sleep(1)

    igniteLogger.logger.info("\n---------------------------------------\nSend Attach Complete to MME\n---------------------------------------")
    s1.sendS1ap('attach_complete', uplinknastransport_attach_complete, enbues1ap_id, nas_attach_complete)

    igniteLogger.logger.info("\n---------------------------------------\nModify Bearer Request received from MME\n---------------------------------------")
    gs.receiveGtp()

    igniteLogger.logger.info("\n---------------------------------------\nSend Modify Bearer Response to MME\n---------------------------------------")
    gs.sendGtp('modify_bearer_response', modify_bearer_response, msg_hierarchy)

    igniteLogger.logger.info("\n---------------------------------------\nEMM Information received from MME\n---------------------------------------")
    s1.receiveS1ap() 
    
    igniteLogger.logger.info("\n---------------------------------------\nUE is Attached\n---------------------------------------")

    time.sleep(2)

    igniteLogger.logger.info("\n---------------------------------------\nSend eRAB Modification Indication to MME\n---------------------------------------")
    s1.sendS1ap('erab_modification_indication', erabmodification_indication, enbues1ap_id)   

    igniteLogger.logger.info("\n---------------------------------------\nModify Bearer Request received from MME\n---------------------------------------")
    gs.receiveGtp()

    igniteLogger.logger.info("\n---------------------------------------\nSend Modify Bearer Response to MME\n---------------------------------------")
    icu.updateKeyValueInDict(modify_bearer_response, "cause_value", 94)
    gs.sendGtp('modify_bearer_response', modify_bearer_response, msg_hierarchy)

    mme_ue_S1AP_id , mme_ue_S1AP_id_present = icu.getKeyValueFromDict(init_ctxt_setup_req, "MME-UE-S1AP-ID")
    mob_ctxt_command = "export LD_LIBRARY_PATH=" + mme_lib_path + " && " + mme_grpc_client_path + "/mme-grpc-client mme-app show mobile-context "+str(mme_ue_S1AP_id)
    mob_ctxt_af_attach = su.executeCommand(mob_ctxt_command,ssh_client)
    icu.mobileContextValidation(str(imsi),mob_ctxt_af_attach)

    proc_stat_af_attach = su.executeCommand(command,ssh_client)

    ue_count_after_attach = int(do.splitProcStats(proc_stat_af_attach, stats_type["subs_attached"]))
    icu.grpcValidation(ue_count_before_attach + 1, ue_count_after_attach, "Number of Subs Attached")

    num_of_erab_mod_ind_af_attach = int(do.splitProcStats(proc_stat_af_attach, stats_type["erab_mod_ind"]))
    icu.grpcValidation(num_of_erab_mod_indication + 1, num_of_erab_mod_ind_af_attach, "Number of ERAB Modification Indication")

    time.sleep(1)
    
    igniteLogger.logger.info ("\n---------------------------------------\nMME send Detach request to UE\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info ("\n---------------------------------------\nDelete Session Request received from MME\n---------------------------------------")
    gs.receiveGtp()

    igniteLogger.logger.info ("\n---------------------------------------\nSend Delete Session Response to MME\n---------------------------------------")
    gs.sendGtp('delete_session_response',delete_session_response,msg_hierarchy)

    igniteLogger.logger.info ("\n---------------------------------------\nMME send Detach Accept to UE\n---------------------------------------")
    s1.sendS1ap('uplinknastransport_detach_accept', uplinknastransport_detach_accept, enbues1ap_id, nas_detach_accept)

    igniteLogger.logger.info ("\n---------------------------------------\neNB receives UE Context Release Request from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info ("\n---------------------------------------\neNB sends UE Context Release Complete to MME\n---------------------------------------")
    s1.sendS1ap('uecontextrelease_complete', uecontextrelease_complete,enbues1ap_id)
 
    print ("\n-------------------------------------\nIMSI Attach eRAB Mod Ind MB Resp Failure Execution Successful\n---------------------------------------")
	
except Exception as e:
    print("**********\nEXCEPTION:"+e.__class__.__name__+"\nError Details : "+str(e)+"\n**********")
    if e.__class__.__name__ != "ConnectionError":
        time.sleep(10)
    igniteLogger.logger.info("\n---------------------------------------\nClearing Buffer\n---------------------------------------")
    icu.clearBuffer()
	
finally:
    if clr_flag == True:
        igniteLogger.logger.info("\n---------------------------------------\nHSS sends CLR to MME\n---------------------------------------")
        ds.sendS6aMsg('cancel_location_request', msg_data_clr, imsi)

        igniteLogger.logger.info("\n---------------------------------------\nHSS receives CLA from MME\n---------------------------------------")
        ds.receiveS6aMsg()
