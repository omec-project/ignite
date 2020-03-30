##
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
*** Settings ***
Suite Setup       Attach Suite Setup
Suite Teardown    Attach Suite Teardown
Resource          ../keywords/robotkeywords/HighLevelKeyword.robot
Resource          ../keywords/robotkeywords/MMEAttachCallflow.robot
Resource          ../keywords/robotkeywords/StringFunctions.robot
*** Test Cases ***
TC1: LTE 4G Auth Response Delay Without Attach
    [Documentation]    Auth Response Delay Without Attach
    [Tags]    TC1    LTE_4G_Auth_Response_Timeout_Without_Attach    Attach    Detach
    [Setup]    Attach Test Setup
    Switch Connection    ${serverID}
    ${procStatOutBfExec1}    Execute Command    pwd
    Log    ${procStatOutBfExec1}
    Switch Connection    ${serverID}
    ${procStatbfExec}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatbfExec}
    ${num_of_auth_resp_timeout}    ${found}    Get Key Value From Dict    ${statsTypes}    auth_resp_timeout
    ${authRespTimeoutCountBf}    Get GRPC Stats Response Count    ${procStatbfExec}    ${num_of_auth_resp_timeout}
    ${authRespTimeoutCountBf}    Convert to Integer    ${authRespTimeoutCountBf}
    Send S1ap    attach_request    ${initUeMessage_AttachReq}    ${enbUeS1APId}    ${nasAttachRequest}    ${IMSI}    #Send Attach Request to MME
    ${air}    Receive S6aMsg    #HSS Receives AIR from MME
    Send S6aMsg    authentication_info_response    ${msgData_aia}    ${IMSI}    #HSS sends AIA to MME
    ${authReqResp}    Receive S1ap    #Auth Request received from MME
    Sleep    5s
    ${intlCntxReleaseCmd}    Receive S1ap    #Initial Context Release Command received from MME
    Send S1ap    ue_context_release_cmp    ${ueContextReleaseCmp}    ${enbUeS1APId}    #eNB sends UE Context Release Complete to MME
    Sleep    1s
    ${procStatAiaTimeOut}    ${stderr}    Execute Command    export LD_LIBRARY_PATH=${openMmeLibPath} && ${mmeGrpcClientPath}/mme-grpc-client mme-app show procedure-stats    timeout=30s    return_stderr=True
    Log    ${procStatAiaTimeOut}
    ${authRespTimeoutCountAf}    Get GRPC Stats Response Count    ${procStatAiaTimeOut}    ${num_of_auth_resp_timeout}
    ${authRespTimeoutCountAf}    Convert to Integer    ${authRespTimeoutCountAf}
    ${incrementauthRespTimeoutCount}    Evaluate    ${authRespTimeoutCountBf}+1
    Should Be Equal    ${incrementauthRespTimeoutCount}    ${authRespTimeoutCountAf}    Expected authResp Count: ${incrementauthRespTimeoutCount}, but Received authResp Count: ${authRespTimeoutCountAf}    values=False
    [Teardown]    Attach Test Teardown