#
# Copyright (c) 2019, Infosys Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");ttach_S1Release.robot
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

*** Settings ***
Suite Setup       Attach Suite Setup
Suite Teardown    Attach Suite Teardown
Resource          ../keywords/robotkeywords/HighLevelKeyword.robot
Resource          ../keywords/robotkeywords/MMEAttachCallflow.robot
Resource          ../keywords/robotkeywords/StringFunctions.robot

*** Test Cases ***
TC1: LTE 4G IMSI Attach Detach
    [Documentation]    Attach Detach success scenario for LTE 4G IMSI
    [Tags]    TC1    LTE_4G_Diameter_Invalid_AVP_Value_response    Attach    Detach
    [Setup]    Attach Test Setup
    Switch Connection    ${serverID}
    ${procStatOutBfExec1}    Execute Command    pwd
    Log    ${procStatOutBfExec1}
    Switch Connection    ${serverID}
    ${procStatOutBfExecUla}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatOutBfExecUla}
    ${numProcessedUla}    Get GRPC Stats Response Count    ${procStatOutBfExecUla}    ${num_of_processed_ula}
    ${numProcessedUla}    Convert to Integer    ${numProcessedUla}
    ${handledEsmInfoResp}    Get GRPC Stats Response Count    ${procStatOutBfExecUla}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoResp}    Convert to Integer    ${handledEsmInfoResp}
    ${processedSecModeResp}    Get GRPC Stats Response Count    ${procStatOutBfExecUla}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeResp}    Convert to Integer    ${processedSecModeResp}
    Send S1ap    ${enbUeS1APId}    attach_request    ${initUeMessage_AttachReq}    ${nasAttachRequest}    ${IMSI}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    ${IMSI}    authentication_info_response    ${msgData_aia}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_sec_mode_cmp    ${uplinkNASTransport_SecModeCmp}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
    ${esmInfoReq}    Receive S1ap    #ESM Information Request from MME
    Send S1ap    ${enbUeS1APId}    esm_information_response    ${uplinknastransport_esm_information_response}    ${nas_esm_information_response}    #ESM Information Response to MME
    ${ulr}    Receive S6aMsg    #HSS receives ULR from MME
    Send S6aMsg    ${IMSI}    update_location_response    ${msg_data_ula_reject}    #HSS sends wrong ULA to MME
    Set Global Variable    ${CLR_Flag}    Yes
    Sleep    5s
    ${attachReject}    Receive S1ap    #Attach Reject
    Sleep    1s
    ${procStatOutAfDetach}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfTO}
    ${numProcessedUlaAf}    Get GRPC Stats Response Count    ${procStatOutAfTO}    ${num_of_processed_ula}
    ${numProcessedUlaAf}    Convert to Integer    ${numProcessedAiaAf}
    Should Be Equal    ${numProcessedUla}    ${numProcessedUlaAf}    Expected number of Processed ula: ${numProcessedUla}, but Received number of Processed ula: ${numProcessedUlaAf}    values=False
    ${procStatOutAfAVP_RESP}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfAVP_RESP}
    ${handledEsmInfoRespAf}    Get GRPC Stats Response Count    ${procStatOutAfAVP_RESP}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoRespAf}    Convert to Integer    ${handledEsmInfoRespAf}
    ${incrementhandledEsmInfoRespCount}    Evaluate    ${handledEsmInfoResp}+1
    Should Be Equal    ${incrementhandledEsmInfoRespCount}    ${handledEsmInfoRespAf}    Expected Esm Info Resp Count: ${incrementhandledEsmInfoRespCount}, but Received Esm Info Resp Count: ${handledEsmInfoRespAf}    values=False
    ${processedSecModeRespAf}    Get GRPC Stats Response Count    ${procStatOutAfAVP_RESP}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeRespAf}    Convert to Integer    ${processedSecModeRespAf}
    ${incProcessedSecModeRespCount}    Evaluate    ${processedSecModeResp}+1
    Should Be Equal    ${incProcessedSecModeRespCount}    ${processedSecModeRespAf}    Expected Sec Mode Resp Count: ${incProcessedSecModeRespCount}, but Received Sec Mode Resp Count: ${processedSecModeRespAf}    values=False
    ${procStatOutBfExec}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatOutBfExec}
    ${ueCountBeforeAttach}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_subscribers_attached}
    ${ueCountBeforeAttach}    Convert to Integer    ${ueCountBeforeAttach}
    ${processed_aia}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_aia}
    ${processed_aia}    Convert to Integer    ${processed_aia}
    ${processed_ula}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_ula}
    ${processed_ula}    Convert to Integer    ${processed_ula}
    ${handledEsmInfoResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoResp}    Convert to Integer    ${handledEsmInfoResp}
    ${processedSecModeResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeResp}    Convert to Integer    ${processedSecModeResp}
    ${processedInitCtxtResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtResp}    Convert to Integer    ${processedInitCtxtResp}
    Send S1ap    ${enbUeS1APId}    attach_request    ${initUeMessage_AttachReq}    ${nasAttachRequest}    ${IMSI}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    ${IMSI}    authentication_info_response    ${msgData_aia}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_sec_mode_cmp    ${uplinkNASTransport_SecModeCmp}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
    ${esmInfoReq}    Receive S1ap    #ESM Information Request from MME
    Send S1ap    ${enbUeS1APId}    esm_information_response    ${uplinknastransport_esm_information_response}    ${nas_esm_information_response}    #ESM Information Response to MME
    ${ulr}    Receive S6aMsg    #HSS receives ULR from MME
    Send S6aMsg    ${IMSI}    update_location_response    ${msgData_ula}    #HSS sends ULA to MME
    ${createSessReqRecdFromMME}    Receive GTP    #Create Session Request received from MME
    Send GTP    create_session_response    ${gtpMsgHeirarchy_tag1}    ${createSessionResp}    #Send Create Session Response to MME
    ${intContSetupReqRec}    Receive S1ap    #Initial Context Setup Request received from MME
    Send S1ap    ${enbUeS1APId}    initial_context_setup_response    ${initContextSetupRes}    #Send Initial Context Setup Response to MME
    Sleep    1s
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_attach_cmp    ${uplinkNASTransport_AttachCmp}    ${nasAttachComplete}    #Send Attach Complete to MME
    ${modBearReqRec}    Receive GTP    #Modify Bearer Request received from MME
    Send GTP    modify_bearer_response    ${gtpMsgHeirarchy_tag2}    ${modifyBearerResp}    #Send Modify Bearer Response to MME
    Sleep    1s
    ${procStatInitCtxtRespAf}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatInitCtxtRespAf}
    ${processedInitCtxtRespAf}    Get GRPC Stats Response Count    ${procStatInitCtxtRespAf}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtRespAf}    Convert to Integer    ${processedInitCtxtRespAf}
    ${incrementProcessedInitCtxtRespCount}    Evaluate    ${processedInitCtxtResp}+1
    Should Be Equal    ${incrementProcessedInitCtxtRespCount}    ${processedInitCtxtRespAf}    Expected Init Ctxt Resp Count: ${incrementProcessedInitCtxtRespCount}, but Received Init Ctxt Resp Count: ${processedInitCtxtRespAf}    values=False
    ${procStatOutAfExec}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfExec}
    ${ueCountAfterAttach}    Get GRPC Stats Response Count    ${procStatOutAfExec}    ${num_of_subscribers_attached}
    ${ueCountAfterAttach}    Convert to Integer    ${ueCountAfterAttach}
    ${incrementUeCount}    Evaluate    ${ueCountBeforeAttach}+1
    Should Be Equal    ${incrementUeCount}    ${ueCountAfterAttach}    Expected UE Attach Count: ${incrementUeCount}, but Received UE Attach Count: ${ueCountAfterAttach}    values=False
    ${procStatOutAfAttachRA}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfAttachRA}
    ${handledEsmInfoRespAf}    Get GRPC Stats Response Count    ${procStatOutAfAttachRA}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoRespAf}    Convert to Integer    ${handledEsmInfoRespAf}
    ${incrementhandledEsmInfoRespCount}    Evaluate    ${handledEsmInfoResp}+1
    Should Be Equal    ${incrementhandledEsmInfoRespCount}    ${handledEsmInfoRespAf}    Expected Esm Info Resp Count: ${incrementhandledEsmInfoRespCount}, but Received Esm Info Resp Count: ${handledEsmInfoRespAf}    values=False
    ${processedSecModeRespAf}    Get GRPC Stats Response Count    ${procStatOutAfAttachRA}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeRespAf}    Convert to Integer    ${processedSecModeRespAf}
    ${incProcessedSecModeRespCount}    Evaluate    ${processedSecModeResp}+1
    Should Be Equal    ${incProcessedSecModeRespCount}    ${processedSecModeRespAf}    Expected Sec Mode Resp Count: ${incProcessedSecModeRespCount}, but Received Sec Mode Resp Count: ${processedSecModeRespAf}    values=False
    ${processed_aiaAf}    Get GRPC Stats Response Count    ${procStatOutAfAttachRA}    ${num_of_processed_aia}
    ${processed_aiaAf}    Convert to Integer    ${processed_aiaAf}
    ${incprocessed_aiaCount}    Evaluate    ${processed_aia}+1
    Should Be Equal    ${incprocessed_aiaCount}    ${processed_aiaAf}    Expected processed aia Count: ${incprocessed_aiaCount}, but Received processed aia Resp Count: ${processed_aiaAf}    values=False
    ${processed_ulaAf}    Get GRPC Stats Response Count    ${procStatOutAfAttachRA}    ${num_of_processed_ula}
    ${processed_ulaAf}    Convert to Integer    ${processed_ulaAf}
    ${incprocessed_ulaAfCount}    Evaluate    ${processed_ula}+1
    Should Be Equal    ${incprocessed_ulaAfCount}    ${processed_ulaAf}    Expected processed ula Count: ${incprocessed_ulaAfCount}, but Received processed ula Count: ${processed_ulaAf}    values=False
    Send S1ap    ${enbUeS1APId}    detach_request    ${uplinkNASTransport_DetachReq}    ${nasDetachRequest}    #Send Detach Request to MME
    ${purgeRequest}    Receive S6aMsg    #HSS receives PUR from MME
    ${delSesReqRec}    Receive GTP    #Delete Session Request received from MME
    Send S6aMsg     purge_response    ${msgData_pua}    ${IMSI}   #HSS sends PUA to MME
    Send GTP    delete_session_response    ${gtpMsgHeirarchy_tag3}    ${deleteSessionResp}    #Send Delete Session Response to MME
    ${detAccUE}    Receive S1ap    #MME send Detach Accept to UE
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ${enbUeS1APId}    ue_context_release_cmp    ${ueContextReleaseCmp}    #eNB sends UE Context Release Complete to MME
    Sleep    1s
    ${procStatOutAfDetachRA}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfDetachRA}
    ${ueCountAfterDetach}    Get GRPC Stats Response Count    ${procStatOutAfDetachRA}    ${num_of_subscribers_attached}
    ${ueCountAfterDetach}    Convert to Integer    ${ueCountAfterDetach}
    Should Be Equal    ${ueCountBeforeAttach}    ${ueCountAfterDetach}    Expected UE Detach Count: ${ueCountBeforeAttach}, but Received UE Detach Count: ${ueCountAfterDetach}    values=False
    [Teardown]    Attach Test Teardown
