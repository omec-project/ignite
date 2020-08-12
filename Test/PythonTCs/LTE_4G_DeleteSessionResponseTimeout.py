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

    print("\n---------------------------------------\nDelete Session Request Timeout Execution Started\n---------------------------------------")

    igniteLogger.logger.info("\n---------------------------------------\nSend Attach Request to MME\n---------------------------------------")
    s1.sendS1ap('attach_request',initial_ue,enbues1ap_id,nas_attach_request,imsi)

    igniteLogger.logger.info("\n---------------------------------------\nHSS receives AIR from MME\n---------------------------------------")
    ds.receiveS6aMsg()

    igniteLogger.logger.info("\n---------------------------------------\nHSS sends AIA to MME\n---------------------------------------")
    ds.sendS6aMsg('authentication_info_response', msg_data_aia,imsi)

    igniteLogger.logger.info("\n---------------------------------------\nAuth Request received from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nSend Auth Response to MME\n---------------------------------------")
    s1.sendS1ap('uplinknastransport_auth_response', uplinknastransport_auth_response, enbues1ap_id, nas_authentication_response)

    igniteLogger.logger.info("\n---------------------------------------\nSecurity Mode Command received from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nSend Security Mode Complete to MME\n---------------------------------------")
    s1.sendS1ap('uplinknastransport_securitymode_complete', uplinknastransport_securitymode_complete, enbues1ap_id, nas_securitymode_complete)

    igniteLogger.logger.info("\n---------------------------------------\nESM Information Request from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\nESM Information Response from MME\n---------------------------------------")
    s1.sendS1ap('esm_information_response', uplinknastransport_esm_information_response, enbues1ap_id, nas_esm_information_response)

    igniteLogger.logger.info("\n---------------------------------------\nHSS receives ULR from MME\n---------------------------------------")
    ds.receiveS6aMsg()

    igniteLogger.logger.info("\n---------------------------------------\nHSS sends ULA to MME\n---------------------------------------")
    ds.sendS6aMsg('update_location_response', msg_data_ula, imsi)

    clr_flag=True

    igniteLogger.logger.info("\n---------------------------------------\nCreate Session Request received from MME\n---------------------------------------")
    gs.receiveGtp()

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

    mme_ue_S1AP_id , mme_ue_S1AP_id_present = icu.getKeyValueFromDict(init_ctxt_setup_req, "MME-UE-S1AP-ID")
    mob_ctxt_command = "export LD_LIBRARY_PATH=" + mme_lib_path + " && " + mme_grpc_client_path + "/mme-grpc-client mme-app show mobile-context "+str(mme_ue_S1AP_id)
    mob_ctxt_af_attach = su.executeCommand(mob_ctxt_command,ssh_client)
    icu.mobileContextValidation(str(imsi),mob_ctxt_af_attach)


    proc_stat_af_attach = su.executeCommand(command,ssh_client)

    ue_count_after_attach = int(do.splitProcStats(proc_stat_af_attach, stats_type["subs_attached"]))
    icu.grpcValidation(ue_count_before_attach + 1, ue_count_after_attach, "Number of Subs Attached")

    igniteLogger.logger.info("\n---------------------------------------\nSend Detach Request to MME\n---------------------------------------")
    s1.sendS1ap('detach_request', uplinknastransport_detach_request, enbues1ap_id, nas_detach_request)

    igniteLogger.logger.info("\n---------------------------------------\nPurge Request received from MME\n---------------------------------------")
    ds.receiveS6aMsg()

    igniteLogger.logger.info("\n---------------------------------------\nDelete Session Request received from MME\n---------------------------------------")
    gs.receiveGtp()

    igniteLogger.logger.info("\n---------------------------------------\nSend Purge Response to MME\n---------------------------------------")
    ds.sendS6aMsg('purge_response', msg_data_pua, imsi) 
    
    igniteLogger.logger.info("\n---------------------------------------\nDelete Session Response Timeout\n---------------------------------------")
    time.sleep(5)

    igniteLogger.logger.info("\n---------------------------------------\nSend Delete Session Response to MME\n---------------------------------------")
    gs.sendGtp('delete_session_response', delete_session_response, msg_hierarchy)

    igniteLogger.logger.info("\n---------------------------------------\nMME send Detach Accept to UE\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\neNB receives UE Context Release Request from MME\n---------------------------------------")
    s1.receiveS1ap()

    igniteLogger.logger.info("\n---------------------------------------\neNB sends UE Context Release Complete to MME\n---------------------------------------")
    s1.sendS1ap('uecontextrelease_complete', uecontextrelease_complete, enbues1ap_id)

    time.sleep(1)
    proc_stat_af_detach = su.executeCommand(command,ssh_client)

    ue_count_after_detach = int(do.splitProcStats(proc_stat_af_detach, stats_type["subs_attached"]))
    icu.grpcValidation(ue_count_before_attach, ue_count_after_detach, "Number of Subs Attached After Detach")

    print("\n---------------------------------------\nDelete Session Request Timeout Execution Successful\n---------------------------------------")
	
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
