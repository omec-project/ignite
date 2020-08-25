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
TC1: LTE 4G Gutti identity response delay
    [Documentation]    LTE 4G Gutti Attach detach
    [Tags]    TC1    LTE_4G_Gutti identity_response_delay    Attach    Detach
    [Setup]    Attach Test Setup
    Switch Connection    ${serverID}
    ${procStatOutBfExec1}    Execute Command    pwd
    Log    ${procStatOutBfExec1}
    Switch Connection    ${serverID}
    #imsi Attach
    ${procStatOutBfExec}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatOutBfExec}
    ${num_of_subscribers_attached}    ${found}    Get Key Value From Dict    ${statsTypes}    subs_attached
    ${ueCountBeforeAttach}    Get GRPC Stats Response Count    ${procStatOutBfExec}    ${num_of_subscribers_attached}
    ${ueCountBeforeAttach}    Convert to Integer    ${ueCountBeforeAttach}
    Send S1ap    ${enbUeS1APId}    attach_request    ${initUeMessage_AttachReq}    ${nasAttachRequest}    ${IMSI}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    ${IMSI}    authentication_info_response    ${msgData_aia}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_secMode_cmp    ${uplinkNASTransport_SecModeCmp}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
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
    ${procStatOutAfExec}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfExec}
    ${ueCountAfterAttach}    Get GRPC Stats Response Count    ${procStatOutAfExec}    ${num_of_subscribers_attached}
    ${ueCountAfterAttach}    Convert to Integer    ${ueCountAfterAttach}
    ${incrementUeCount}    Evaluate    ${ueCountBeforeAttach}+1
    Should Be Equal    ${incrementUeCount}    ${ueCountAfterAttach}    Expected UE Attach Count: ${incrementUeCount}, but Received UE Attach Count: ${ueCountAfterAttach}    values=False
    Send S1ap    ${enbUeS1APId}    detach_request    ${uplinkNASTransport_DetachReq}    ${nasDetachRequest}    #Send Detach Request to MME
    ${purgeRequest}    Receive S6aMsg    #HSS receives PUR from MME
    ${delSesReqRec}    Receive GTP    #Delete Session Request received from MME
    Send S6aMsg     purge_response    ${msgData_pua}    ${IMSI}   #HSS sends PUA to MME
    Send GTP    delete_session_response    ${gtpMsgHeirarchy_tag3}    ${deleteSessionResp}    #Send Delete Session Response to MME
    ${detAccUE}    Receive S1ap    #MME send Detach Accept to UE
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ${enbUeS1APId}    ue_context_release_cmp    ${ueContextReleaseCmp}    #eNB sends UE Context Release Complete to MME
    ${procStatOutAfDetach}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfDetach}
    ${ueCountAfterDetach}    Get GRPC Stats Response Count    ${procStatOutAfDetach}    ${num_of_subscribers_attached}
    ${ueCountAfterDetach}    Convert to Integer    ${ueCountAfterDetach}
    Should Be Equal    ${ueCountBeforeAttach}    ${ueCountAfterDetach}    Expected UE Detach Count: ${ueCountBeforeAttach}, but Received UE Detach Count: ${ueCountAfterDetach}    values=False
    Send S6aMsg    ${IMSI}    cancel_location_request    ${msgData_clr}    #HSS sends clr to mme
    ${cla}    Receive S6aMsg    #HSS recevies from mme
    #guti Identity response delay
    Send S1ap    ${enbUeS1APId}    attach_request_guti    ${initialUeGuti}    ${nasAttachRequestGuti}    ${guti_invalid}    #Send Attach Request to MME
    ${identity_req}    Receive S1ap    #Identity Request received from MME
    Sleep    5s
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ${enbUeS1APId}    ue_context_release_cmp    ${ueContextReleaseCmp}    #eNB sends UE Context Release Complete to MME
    Send S1ap    ${enbUeS1APId}    attach_request_guti    ${initialUeGuti}    ${nasAttachRequestGuti}    ${guti_invalid}    #Send Attach Request to MME
    ${identity_req}    Receive S1ap    #Identity Request received from MME
	
    Send S1ap    ${enbUeS1APId}    identity_response    ${uplinknastransport_identity_response}    ${nas_identity_response}    ${IMSI}    #Send Identity Response to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    ${IMSI}    authentication_info_response    ${msgData_aia}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_authresp    ${uplinkNASTransport_AuthResp}    ${nasAuthenticationResponse}    #Send Auth Response to MME
    ${secModeCmdRecd}    Receive S1ap    #Security Mode Command received from MME
    Send S1ap    ${enbUeS1APId}    uplink_nas_transport_secMode_cmp    ${uplinkNASTransport_SecModeCmp}    ${nasSecurityModeComplete}    #Send Security Mode Complete to MME
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
    ${procStatOutAfExecGuti}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfExecGuti}
    ${ueCountAfterAttach}    Get GRPC Stats Response Count    ${procStatOutAfExecGuti}    ${num_of_subscribers_attached}
    ${ueCountAfterAttach}    Convert to Integer    ${ueCountAfterAttach}
    ${incrementUeCount}    Evaluate    ${ueCountBeforeAttach}+1
    Should Be Equal    ${incrementUeCount}    ${ueCountAfterAttach}    Expected UE Attach Count: ${incrementUeCount}, but Received UE Attach Count: ${ueCountAfterAttach}    values=False
    Send S1ap    ${enbUeS1APId}    detach_request    ${uplinkNASTransport_DetachReq}    ${nasDetachRequest}    #Send Detach Request to MME
    ${pur}    Receive S6aMsg    #HSS receives PUR from MME
    ${delSesReqRec}    Receive GTP    #Delete Session Request received from MME
    Send S6aMsg     purge_UE_answer    ${msgData_pua}    ${IMSI}   #HSS sends PUA to MME
    Send GTP    delete_session_response    ${gtpMsgHeirarchy_tag3}    ${deleteSessionResp}    #Send Delete Session Response to MME
    ${detAccUE}    Receive S1ap    #MME send Detach Accept to UE
    ${eNBUeRelReqFromMME}    Receive S1ap    #eNB receives UE Context Release Request from MME
    Send S1ap    ${enbUeS1APId}    ue_context_release_cmp    ${ueContextReleaseCmp}    #eNB sends UE Context Release Complete to MME
    ${procStatOutAfDetachGuti}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s
    Log    ${procStatOutAfDetachGuti}
    ${ueCountAfterDetach}    Get GRPC Stats Response Count    ${procStatOutAfDetachGuti}    ${num_of_subscribers_attached}
    ${ueCountAfterDetach}    Convert to Integer    ${ueCountAfterDetach}
    Should Be Equal    ${ueCountBeforeAttach}    ${ueCountAfterDetach}    Expected UE Detach Count: ${ueCountBeforeAttach}, but Received UE Detach Count: ${ueCountAfterDetach}    values=False
    Send S6aMsg    ${IMSI}    cancel_location_request    ${msgData_clr}    #HSS sends clr to mme
    ${cla}    Receive S6aMsg    #HSS recevies from mme
    [Teardown]    Attach Test Teardown


