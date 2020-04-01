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
TC1: LTE 4G IMSI Guti Attach detach
    [Documentation]    LTE 4G Gutti Attach detach
    [Tags]    TC1    LTE_4G_IMSI_Guti_Attach_detach    Attach    Detach
    [Setup]    Attach Test Setup
    Switch Connection    ${serverID}
    ${procStatOutBfExec1}    Execute Command    pwd
    Log    ${procStatOutBfExec1}
    Switch Connection    ${serverID}
    ${procStatOutBfExec}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatOutBfExec}
    ${num_of_handled_esm_info_resp}    ${found}    Get Key Value From Dict    ${statsTypes}    esm_info_resp
    ${handledEsmInfoResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoResp}    Convert to Integer    ${handledEsmInfoResp}
    ${num_of_processed_sec_mode_resp}    ${found}    Get Key Value From Dict    ${statsTypes}    processed_sec_mode
    ${processedSecModeResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeResp}    Convert to Integer    ${processedSecModeResp}
    ${num_of_processed_init_ctxt_resp}    ${found}    Get Key Value From Dict    ${statsTypes}    init_ctxt_resp
    ${processedInitCtxtResp}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtResp}    Convert to Integer    ${processedInitCtxtResp}
    ${num_of_subscribers_attached}    ${found}    Get Key Value From Dict    ${statsTypes}    subs_attached
    ${ueCountBeforeAttach}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_subscribers_attached}
    ${ueCountBeforeAttach}    Convert to Integer    ${ueCountBeforeAttach}
    ${num_of_processed_aia}    ${found}    Get Key Value From Dict    ${statsTypes}    processed_aia
    ${processed_aia}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_aia}
    ${processed_aia}    Convert to Integer    ${processed_aia}
    ${num_of_processed_ula}    ${found}    Get Key Value From Dict    ${statsTypes}    processed_ula
    ${processed_ula}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_processed_ula}
    ${processed_ula}    Convert to Integer    ${processed_ula}
    Send S1ap    attach_request    ${initUeMessage_AttachReq}    ${enbUeS1APId}    ${nasAttachRequest}    ${IMSI}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    authentication_info_response    ${msgData_aia}    ${IMSI}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${enbUeS1APId}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    uplink_nas_transport_secMode_cmp    ${uplinkNASTransport_SecModeCmp}    ${enbUeS1APId}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
    ${esmInfoReq}    Receive S1ap    #ESM Information Request from MME
    Send S1ap    esm_information_response    ${uplinknastransport_esm_information_response}    ${enbUeS1APId}    ${nas_esm_information_response}    #ESM Information Response to MME
    ${ulr}    Receive S6aMsg    #HSS receives ULR from MME
    Send S6aMsg     update_location_response    ${msgData_ula}    ${IMSI}   #HSS sends ULA to MME
    Set Global Variable    ${CLR_Flag}    Yes
    ${createSessReqRecdFromMME}    Receive GTP    #Create Session Request received from MME
    Send GTP    create_session_response    ${createSessionResp}    ${gtpMsgHeirarchy_tag1}    #Send Create Session Response to MME
    ${intContSetupReqRec}    Receive S1ap    #Initial Context Setup Request received from MME
    Send S1ap    initial_context_setup_response    ${initContextSetupRes}    ${enbUeS1APId}    #Send Initial Context Setup Response to MME
    Sleep    1s
    Send S1ap    uplink_nas_transport_attach_cmp    ${uplinkNASTransport_AttachCmp}    ${enbUeS1APId}    ${nasAttachComplete}    #Send Attach Complete to MME
    ${modBearReqRec}    Receive GTP    #Modify Bearer Request received from MME
    Send GTP    modify_bearer_response    ${modifyBearerResp}    ${gtpMsgHeirarchy_tag2}    #Send Modify Bearer Response to MME
    ${recEMMInfo}    Receive S1ap    #EMM Information received from MME
    Sleep    1s
    ${mmeUeS1APId}    ${mmeUeS1APIdPresent}    Get Key Value From Dict    ${intContSetupReqRec}    MME-UE-S1AP-ID
    ${IMSI_str}    Convert to String    ${IMSI}
    ${mobContextAftExec}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show mobile-context ${mmeUeS1APId}    timeout=30s
    Log    ${mobContextAftExec}
    Should Contain    ${mobContextAftExec}    ${IMSI_str}    Expected IMSI: ${IMSI_str}, but Received ${mobContextAftExec}    values=False
    Should Contain    ${mobContextAftExec}    EpsAttached    Expected UE State: EpsAttached, but Received ${mobContextAftExec}    values=False
    ${procStatOutAfExec}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfExec}
    ${processedInitCtxtRespAf}    Get GRPC Stats Response Count    ${procStatOutAfExec}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtRespAf}    Convert to Integer    ${processedInitCtxtRespAf}
    ${incrementProcessedInitCtxtRespCount}    Evaluate    ${processedInitCtxtResp}+1
    Should Be Equal    ${incrementProcessedInitCtxtRespCount}    ${processedInitCtxtRespAf}    Expected Init Ctxt Resp Count: ${incrementProcessedInitCtxtRespCount}, but Received Init Ctxt Resp Count: ${processedInitCtxtRespAf}    values=False
    ${ueCountAfterAttach}    Get GRPC Stats Response Count    ${procStatOutAfExec}    ${num_of_subscribers_attached}
    ${ueCountAfterAttach}    Convert to Integer    ${ueCountAfterAttach}
    ${incrementUeCount}    Evaluate    ${ueCountBeforeAttach}+1
    Should Be Equal    ${incrementUeCount}    ${ueCountAfterAttach}    Expected UE Attach Count: ${incrementUeCount}, but Received UE Attach Count: ${ueCountAfterAttach}    values=False
    ${procStatOutAfDetach}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfDetach}
    ${handledEsmInfoRespAf}    Get GRPC Stats Response Count    ${procStatOutAfDetach}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoRespAf}    Convert to Integer    ${handledEsmInfoRespAf}
    ${incrementhandledEsmInfoRespCount}    Evaluate    ${handledEsmInfoResp}+1
    Should Be Equal    ${incrementhandledEsmInfoRespCount}    ${handledEsmInfoRespAf}    Expected Esm Info Resp Count: ${incrementhandledEsmInfoRespCount}, but Received Esm Info Resp Count: ${handledEsmInfoRespAf}    values=False
    ${processedSecModeRespAf}    Get GRPC Stats Response Count    ${procStatOutAfDetach}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeRespAf}    Convert to Integer    ${processedSecModeRespAf}
    ${incProcessedSecModeRespCount}    Evaluate    ${processedSecModeResp}+1
    Should Be Equal    ${incProcessedSecModeRespCount}    ${processedSecModeRespAf}    Expected Sec Mode Resp Count: ${incProcessedSecModeRespCount}, but Received Sec Mode Resp Count: ${processedSecModeRespAf}    values=False
    ${processed_aiaAf}    Get GRPC Stats Response Count    ${procStatOutAfDetach}    ${num_of_processed_aia}
    ${processed_aiaAf}    Convert to Integer    ${processed_aiaAf}
    ${incprocessed_aiaCount}    Evaluate    ${processed_aia}+1
    Should Be Equal    ${incprocessed_aiaCount}    ${processed_aiaAf}    Expected processed aia Count: ${incprocessed_aiaCount}, but Received processed aia Resp Count: ${processed_aiaAf}    values=False
    ${processed_ulaAf}    Get GRPC Stats Response Count    ${procStatOutAfDetach}    ${num_of_processed_ula}
    ${processed_ulaAf}    Convert to Integer    ${processed_ulaAf}
    ${incprocessed_ulaAfCount}    Evaluate    ${processed_ula}+1
    Should Be Equal    ${incprocessed_ulaAfCount}    ${processed_ulaAf}    Expected processed ula Count: ${incprocessed_ulaAfCount}, but Received processed ula Count: ${processed_ulaAf}    values=False
    Send S1ap    detach_request    ${uplinkNASTransport_DetachReq}    ${enbUeS1APId}    ${nasDetachRequest}    #Send Detach Request to MME
    ${delSesReqRec}    Receive GTP    #Delete Session Request received from MME
    Send GTP    delete_session_response    ${deleteSessionResp}    ${gtpMsgHeirarchy_tag3}    #Send Delete Session Response to MME
    ${detAccUE}    Receive S1ap    #MME send Detach Accept to UE
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ue_context_release_cmp    ${ueContextReleaseCmp}    ${enbUeS1APId}    #eNB sends UE Context Release Complete to MME
    Sleep    1s
    ${procStatOutAfImsiDetach}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfImsiDetach}
    ${ueCountAfterDetach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_subscribers_attached}
    ${ueCountAfterDetach}    Convert to Integer    ${ueCountAfterDetach}
    Should Be Equal    ${ueCountBeforeAttach}    ${ueCountAfterDetach}    Expected UE Detach Count: ${ueCountBeforeAttach}, but Received UE Detach Count: ${ueCountAfterDetach}    values=False
    ${ueCountBeforeGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_subscribers_attached}
    ${ueCountBeforeGutiAttach}    Convert to Integer    ${ueCountBeforeGutiAttach}
    ${handledEsmInfoRespBefGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoRespBefGutiAttach}    Convert to Integer    ${handledEsmInfoRespBefGutiAttach}
    ${processedSecModeRespBefGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeRespBefGutiAttach}    Convert to Integer    ${processedSecModeRespBefGutiAttach}
    ${processedInitCtxtRespBefGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtRespBefGutiAttach}    Convert to Integer    ${processedInitCtxtRespBefGutiAttach}
    ${processed_aiaBefGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_processed_aia}
    ${processed_aiaBefGutiAttach}    Convert to Integer    ${processed_aiaBefGutiAttach}
    ${processed_ulaBefGutiAttach}    Get GRPC Stats Response Count    ${procStatOutAfImsiDetach}    ${num_of_processed_ula}
    ${processed_ulaBefGutiAttach}    Convert to Integer    ${processed_ulaBefGutiAttach}
    Send S1ap    attach_request_guti    ${initialUeGuti}    ${enbUeS1APId}    ${nasAttachRequestGuti}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    authentication_info_response    ${msgData_aia}    ${IMSI}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${enbUeS1APId}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    uplink_nas_transport_secMode_cmp    ${uplinkNASTransport_SecModeCmp}    ${enbUeS1APId}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
    ${esmInfoReq}    Receive S1ap    #ESM Information Request from MME
    Send S1ap    esm_information_response    ${uplinknastransport_esm_information_response}    ${enbUeS1APId}    ${nas_esm_information_response}    #ESM Information Response to MME
    ${ulr}    Receive S6aMsg    #HSS receives ULR from MME
    Send S6aMsg     update_location_response    ${msgData_ula}    ${IMSI}   #HSS sends ULA to MME
    ${createSessReqRecdFromMME}    Receive GTP    #Create Session Request received from MME
    Send GTP    create_session_response    ${createSessionResp}    ${gtpMsgHeirarchy_tag1}    #Send Create Session Response to MME
    ${intContSetupReqRec}    Receive S1ap    #Initial Context Setup Request received from MME
    Send S1ap    initial_context_setup_response    ${initContextSetupRes}    ${enbUeS1APId}    #Send Initial Context Setup Response to MME
    Sleep    1s
    Send S1ap    uplink_nas_transport_attach_cmp    ${uplinkNASTransport_AttachCmp}    ${enbUeS1APId}    ${nasAttachComplete}    #Send Attach Complete to MME
    ${modBearReqRec}    Receive GTP    #Modify Bearer Request received from MME
    Send GTP    modify_bearer_response    ${modifyBearerResp}    ${gtpMsgHeirarchy_tag2}    #Send Modify Bearer Response to MME
    Sleep    2s
    ${mmeUeS1APId}    ${mmeUeS1APIdPresent}    Get Key Value From Dict    ${intContSetupReqRec}    MME-UE-S1AP-ID
    ${IMSI_str}    Convert to String    ${IMSI}
    ${mobContextAftExecReattach}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show mobile-context ${mmeUeS1APId}    timeout=30s
    Log    ${mobContextAftExecReattach}
    Should Contain    ${mobContextAftExecReattach}    ${IMSI_str}    Expected IMSI: ${IMSI_str}, but Received ${mobContextAftExecReattach}    values=False
    Should Contain    ${mobContextAftExecReattach}    EpsAttached    Expected UE State: EpsAttached, but Received ${mobContextAftExecReattach}    values=False
    ${procStatAfAttachGuti}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatAfAttachGuti}
    ${ueCountAfterGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_subscribers_attached}
    ${ueCountAfterGutiAttach}    Convert to Integer    ${ueCountAfterGutiAttach}
    ${incrementUeCountAfterGutiAttach}    Evaluate    ${ueCountBeforeGutiAttach}+1
    Should Be Equal    ${incrementUeCountAfterGutiAttach}    ${ueCountAfterGutiAttach}    Expected UE Attach Count: ${incrementUeCountAfterGutiAttach}, but Received UE Attach Count: ${ueCountAfterGutiAttach}    values=False
    ${processedInitCtxtRespAfGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_processed_init_ctxt_resp}
    ${processedInitCtxtRespAfGutiAttach}    Convert to Integer    ${processedInitCtxtRespAfGutiAttach}
    ${incrementProcessedInitCtxtRespCountGutiAttach}    Evaluate    ${processedInitCtxtRespBefGutiAttach}+1
    Should Be Equal    ${incrementProcessedInitCtxtRespCountGutiAttach}    ${processedInitCtxtRespAfGutiAttach}    Expected Init Ctxt Resp Count: ${incrementProcessedInitCtxtRespCountGutiAttach}, but Received Init Ctxt Resp Count: ${processedInitCtxtRespAfGutiAttach}    values=False
    ${handledEsmInfoRespAfGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_handled_esm_info_resp}
    ${handledEsmInfoRespAfGutiAttach}    Convert to Integer    ${handledEsmInfoRespAfGutiAttach}
    ${incrementhandledEsmInfoRespCountGutiAttach}    Evaluate    ${handledEsmInfoRespBefGutiAttach}+1
    Should Be Equal    ${incrementhandledEsmInfoRespCountGutiAttach}    ${handledEsmInfoRespAfGutiAttach}    Expected Esm Info Resp Count: ${incrementhandledEsmInfoRespCountGutiAttach}, but Received Esm Info Resp Count: ${handledEsmInfoRespAfGutiAttach}    values=False
    ${processedSecModeRespAfGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_processed_sec_mode_resp}
    ${processedSecModeRespAfGutiAttach}    Convert to Integer    ${processedSecModeRespAfGutiAttach}
    ${incProcessedSecModeRespCountGutiAttach}    Evaluate    ${processedSecModeRespBefGutiAttach}+1
    Should Be Equal    ${incProcessedSecModeRespCountGutiAttach}    ${processedSecModeRespAfGutiAttach}    Expected Sec Mode Resp Count: ${incProcessedSecModeRespCountGutiAttach}, but Received Sec Mode Resp Count: ${processedSecModeRespAfGutiAttach}    values=False
    ${processed_aiaAfGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_processed_aia}
    ${processed_aiaAfGutiAttach}    Convert to Integer    ${processed_aiaAfGutiAttach}
    ${incprocessed_aiaCountGutiAttach}    Evaluate    ${processed_aiaBefGutiAttach}+1
    Should Be Equal    ${incprocessed_aiaCountGutiAttach}    ${processed_aiaAfGutiAttach}    Expected processed aia Count: ${incprocessed_aiaCountGutiAttach}, but Received processed aia Resp Count: ${processed_aiaAfGutiAttach}    values=False
    ${processed_ulaAfGutiAttach}    Get GRPC Stats Response Count    ${procStatAfAttachGuti}    ${num_of_processed_ula}
    ${processed_ulaAfGutiAttach}    Convert to Integer    ${processed_ulaAfGutiAttach}
    ${incprocessed_ulaAfCountGutiAttach}    Evaluate    ${processed_ulaBefGutiAttach}+1
    Should Be Equal    ${incprocessed_ulaAfCountGutiAttach}    ${processed_ulaAfGutiAttach}    Expected processed ula Count: ${incprocessed_ulaAfCountGutiAttach}, but Received processed ula Count: ${processed_ulaAfGutiAttach}    values=False
    Send S1ap    detach_request    ${uplinkNASTransport_DetachReq}    ${enbUeS1APId}    ${nasDetachRequest}    #Send Detach Request to MME
    ${delSesReqRec}    Receive GTP    #Delete Session Request received from MME
    Send GTP    delete_session_response    ${deleteSessionResp}    ${gtpMsgHeirarchy_tag3}    #Send Delete Session Response to MME
    ${detAccUE}    Receive S1ap    #MME send Detach Accept to UE
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ue_context_release_cmp    ${ueContextReleaseCmp}    ${enbUeS1APId}    #eNB sends UE Context Release Complete to MME
    Sleep    2s
    ${procStatOutAfDetachGuti}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfDetachGuti}
    ${ueCountAfterGutiDetach}    Get GRPC Stats Response Count    ${procStatOutAfDetachGuti}    ${num_of_subscribers_attached}
    ${ueCountAfterGutiDetach}    Convert to Integer    ${ueCountAfterGutiDetach}
    Should Be Equal    ${ueCountBeforeGutiAttach}    ${ueCountAfterGutiDetach}    Expected UE Detach Count: ${ueCountBeforeGutiAttach}, but Received UE Detach Count: ${ueCountAfterGutiDetach}    values=False
    [Teardown]    Attach Test Teardown
    
