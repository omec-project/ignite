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

*** Settings ***
Documentation     User defined Keyword file for MME Attach Call flow. Only keywords related to Attach call flow should go in to this file.
Resource          HighLevelKeyword.robot
Resource          ../../resources/resources.MMEConfig.txt
Resource          StringFunctions.robot

*** Keywords ***
Login to MME Machine
    [Documentation]    Login in to the MME Machine. ${mmeServerIP}, ${mmeUserName) variables defined in resurces.MMEConfig.txt file. ${mmePassword} is taken as userinput while executing run.sh script.
    ${serverID}    Open Connection    ${mmeServerIP}
    Login    ${mmeUserName}    ${mmePassword}
    [Return]    ${serverID}

Login to Ignite Machine
    [Documentation]    Login in to the Ignite Machine. ${igniteServerIP}, ${igniteUserName) variables defined in resurces.MMEConfig.txt file. ${ignitePassword} is taken as userinput while executing run.sh script.
    ${serverIDIgnite}    Open Connection    ${igniteServerIP}
    Login    ${igniteUserName}    ${ignitePassword}
    [Return]    ${serverIDIgnite}

Execute Command in MME
    [Arguments]    ${cmdtoexecute}    ${serverID}
    [Documentation]    Used for exeucting any linux/unix command in shell. Arguments taken are ${cmdtoexecute} and ${serverID} from Login to MME Machine
    Switch Connection    ${serverID}
    ${output}    Execute Command    ${cmdtoexecute}
    Sleep    3s
    [Return]    ${output}

Attach Suite Setup
    [Documentation]    This is the first keyword executed when execution is triggered. Below prerequisites are achived with this keyword
    ...
    ...    * \ Loads all the required json files in to variables
    ...    * \ Login to MME machine
    ...    * Creates suite level tcpdump file
    ...    * Creates s1ap,gtp,diameter sockets
    ${defaultS1SetupReq}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/s1setup_request.json
    ${initUeMessage_AttachReq}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/initial_uemessage.json
    ${initUeServiceReq}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/init_ue_servicerequest.json
    ${uplinkNASTransport_AuthResp}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_authresp.json
    ${uplinkNASTransport_SecModeCmp}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_securitymodecmp.json
    ${initContextSetupRes}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/initialcontextsetup_response.json
    ${uplinkNASTransport_AttachCmp}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_attachcmp.json
    ${uplinkNASTransport_DetachAcp}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_detachaccept.json
    ${uplinkNASTransport_DetachReq}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_detachrequest.json
    ${uplinknastransport_esm_information_response}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_esm_information_response.json
    ${ueContextReleaseCmp}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uecontextrelease_complete.json
    ${ueContextReleaseCmd}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uecontextrelease_command.json
    ${initialUeGuti}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/initial_uemessage_guti.json
    ${uplinknastransport_identity_response}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uplinknastransport_identityresp.json
    ${nasAttachRequest}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/attach_request.json
    ${nasServiceRequest}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/service_request.json
    ${nasDetachAccept}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/detach_accept.json
    ${nasAuthenticationResponse}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/authentication_response.json
    ${nasSecurityModeComplete}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/security_mode_complete.json
    ${nasAttachComplete}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/attach_complete.json
    ${nasDetachRequest}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/detach_request.json
    ${nasAttachRequestGuti}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/attach_request_guti.json
    ${nas_identity_response}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/identity_response.json
    ${nas_esm_information_response}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/NAS/esm_information_response.json
    ${ueContextReleaseRequest}    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/S1AP/uecontextrelease_request.json
    ${gtpMsgHeirarchy_tag1}    ${createSessionResp}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/GTP/create_session_response.json
    ${gtpMsgHeirarchy_tag2}    ${modifyBearerResp}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/GTP/modify_bearer_response.json
    ${gtpMsgHeirarchy_tag3}    ${deleteSessionResp}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/GTP/delete_session_response.json
    ${gtpMsgHeirarchy_tag4}    ${releaseBearerResponse}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/GTP/release_access_bearers_response.json
    ${protocol_aia}    ${msgData_aia}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/aia.json
    ${msgDataAiaFail}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/aia_failure.json
    ${protocol_ula}    ${msgData_ula}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/ula.json
    ${gtpMsgHeirarchy_tag5}    ${downlinkDataNotification}    Load Templates From File   ${CURDIR}/../../../MessageTemplates/GTP/downlink_data_notification.json
    ${protocol_clr}    ${msgData_clr}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/clr.json
    ${msgDataUlaFail}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/ula_failure.json
    ${msgDataAiaFail}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/aia_failure.json
    ${protocol_pua}    ${msgData_pua}    Load Templates From File    ${CURDIR}/../../../MessageTemplates/Diameter/pua.json
    ${statsTypes}    Load JSON Data From File    ${CURDIR}/../../support_utilities/statsTypes.json
    Set Suite Variable    ${statsTypes}
    Set Suite Variable    ${uplinknastransport_identity_response}
    Set Suite Variable    ${nas_esm_information_response}
    Set Suite Variable    ${uplinknastransport_esm_information_response}
    Set Suite Variable    ${initialUeGuti}
    Set Suite Variable    ${nasAttachRequestGuti}
    Set Suite Variable    ${nas_identity_response}
    Set Suite Variable    ${initUeServiceReq}
    Set Suite Variable    ${nasServiceRequest}
    Set Suite Variable    ${defaultS1SetupReq}
    Set Suite Variable    ${initUeMessage_AttachReq}
    Set Suite Variable    ${uplinkNASTransport_AuthResp}
    Set Suite Variable    ${uplinkNASTransport_SecModeCmp}
    Set Suite Variable    ${initContextSetupRes}
    Set Suite Variable    ${uplinkNASTransport_AttachCmp}
    Set Suite Variable    ${ueContextReleaseRequest}
    Set Suite Variable    ${ueContextReleaseCmd}
    Set Suite Variable    ${gtpMsgHeirarchy_tag1}
    Set Suite Variable    ${gtpMsgHeirarchy_tag2}
    Set Suite Variable    ${createSessionResp}
    Set Suite Variable    ${modifyBearerResp}
    Set Suite Variable    ${uplinkNASTransport_DetachReq}
    Set Suite Variable    ${uplinkNASTransport_DetachAcp}
    Set Suite Variable    ${ueContextReleaseCmp}
    Set Suite Variable    ${gtpMsgHeirarchy_tag3}
    Set Suite Variable    ${deleteSessionResp}
    Set Suite Variable    ${gtpMsgHeirarchy_tag4}
    Set Suite Variable    ${releaseBearerResponse}
    Set Suite Variable    ${protocol_aia}
    Set Suite Variable    ${protocol_ula}
    Set Suite Variable    ${protocol_clr}
    Set Suite Variable    ${protocol_pua}
    Set Suite Variable    ${msgData_aia}
    Set Suite Variable    ${msgDataAiaFail}
    Set Suite Variable    ${msgData_ula}
    Set Suite Variable    ${msgData_clr}
    Set Suite Variable    ${msgData_pua}
    Set Suite Variable    ${msgDataUlaFail}
    Set Suite Variable    ${nasAttachRequest}
    Set Suite Variable    ${nasDetachAccept}
    Set Suite Variable    ${nasAuthenticationResponse}
    Set Suite Variable    ${nasSecurityModeComplete}
    Set Suite Variable    ${nasAttachComplete}
    Set Suite Variable    ${nasDetachRequest}
    Set Suite Variable    ${downlinkDataNotification}
    Set Suite Variable    ${gtpMsgHeirarchy_tag5}
    ${serverID}    Login to MME Machine
    Set Global Variable    ${serverID}
    Switch Connection    ${serverID}
    ${homepathmme}    Execute Command    pwd
    ${suitename}    Edit Test Suite or Test Case Name    Suite
    ${serverIDIgnite}    Login to Ignite Machine
    Set Global Variable    ${serverIDIgnite}
    Switch Connection    ${serverIDIgnite}
    ${homepathignite}    Execute Command    pwd
    ${mmesuiteprocid}    Start Process    echo ${ignitePassword} | sudo -S tcpdump -i any -w ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/${suitename}_tcpdump.pcap    shell=yes
    Switch Connection    ${serverIDIgnite}
    Execute Command    echo ${ignitePassword} | sudo -S chmod 777 ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}
    Set Global Variable    ${homepathignite}
    Set Global Variable    ${homepathmme}
    Set Global Variable    ${mmesuiteprocid}
    Set Global Variable    ${suitename}
    

Attach Suite Teardown
    [Documentation]    This keyword gets executed as a last step of suite execution. This keyword closes all the created sockets, kills the tcpdump created and modifies the tcpdump privilages.
    Switch Connection    ${serverIDIgnite}
    Terminate Process    ${mmesuiteprocid}    kill
    Run Process    cd ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/ && chmod 777 ${suitename}_tcpdump.pcap    shell=yes

Attach Test Setup
    [Documentation]    This keyword gets executed as prerequisite before actual test case execution starts. \ Mmelog file is capturing and testcase level tcpdump capturing starts as part of this keyword.
    ${tcname}    Edit Test Suite or Test Case Name    Testcase
    Switch Connection    ${serverID}
    ${mmelogprosid}    Execute Command    tail -f /tmp/mmelogs.txt > /tmp/${tcname}_mmelog.txt &
    ${prosid}    Execute Command    ps -ef | grep tail | grep -v grep | awk '{print $2}'
    #${mmelogprosid}    Start Process    tail -f /tmp/mmelogs.txt > ${homepathmme}/LOGS/${suitename}/${suitenamecmdline}/${tcname}_mmelog.txt    shell=yes
    Switch Connection    ${serverIDIgnite}
    ${mmetestcasepcapprocid}    Start Process    echo ${ignitePassword} | sudo -S nohup tcpdump -i any -w ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/${tcname}_tcpdump.pcap    shell=yes
    ${IMSI}    Generate Unique Id    imsi
    ${gTP-TEID}    Generate Unique Id    gTP-TEID
    ${guti_invalid}    Generate Unique Id    guti_invalid
    ${enbUeS1APId}    Generate Unique Id    enbues1apid
    Set Global Variable    ${IMSI}
    Set Global Variable    ${gTP-TEID}
    Set Global Variable    ${guti_invalid}
    Set Global Variable    ${prosid}
    Set Global Variable    ${enbUeS1APId}
    Set Global Variable    ${mmetestcasepcapprocid}
    Set Global Variable    ${tcname}
    Set Global Variable    ${mmelogprosid}
    Set Global Variable    ${CLR_Flag}    No

Attach Test Teardown
    [Documentation]    This is the last executed keyword of a testcase. This keyword kills the mmelog and tcpdump backgroud process.
    ...
    ...    This keyword also modifies the tcpdump privilage and creates a zip file with mme log and testcase level tcpdump
    Run Keyword If    '${CLR_Flag}'=='Yes'    Send S6aMsg    cancel_location_request    ${msgData_clr}    ${IMSI}    #HSS sends clr to mme
    Run Keyword If    '${CLR_Flag}'=='Yes'    Receive S6aMsg    #HSS recevies from mme
    Run Keyword If    '${TEST STATUS}'=='FAIL'    Sleep    10s
    Clear Buffer 
    Switch Connection    ${serverID}
    Execute Command    kill -9 ${prosid}
    #Terminate Process    ${mmelogprosid}    kill
    Execute Command    sshpass -p "${ignitePassword}" scp -o StrictHostKeyChecking=no /tmp/${tcname}_mmelog.txt ${igniteUserName}@${igniteServerIP}:${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/
    Execute Command    rm -rf /tmp/${tcname}_mmelog.txt
    Switch Connection    ${serverIDIgnite}
    Sleep    2s
    Terminate Process    ${mmetestcasepcapprocid}    kill
    Run Process    cd ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/ && chmod 777 ${tcname}_tcpdump.pcap    shell=yes
    Run Process    cd ${homepathignite}/LOGS/${suitename}/${suitenamecmdline}/ && zip -r ${tcname}.zip ${tcname}_tcpdump.pcap ${tcname}_mmelog.txt && echo ${ignitePassword} | sudo -S rm ${tcname}_tcpdump.pcap ${tcname}_mmelog.txt    shell=yes
    ${IMSI}    Convert to Integer    ${IMSI}

Propogate Parameter from Request to Answer Diameter
    [Arguments]    ${air_ulr}    ${msgData_aia_ulr}
    [Documentation]    This keyword propogates parameter from request to answer diameter. Arguments to passed ${air_ulr} ${msgData_aia_ulr}, this keyword returns ${msgData_aia_ulr} data
    ${sessionId}    Get    ${air_ulr}    diameter    session-id
    ${hbh}    Get    ${air_ulr}    diameter    hop-by-hop-identifier
    ${ete}    Get    ${air_ulr}    diameter    end-to-end-identifier
    ${msgData_aia_ulr}    Replace    ${msgData_aia_ulr}    diameter    session-id    ${sessionId}
    ${msgData_aia_ulr}    Replace    ${msgData_aia_ulr}    diameter    hop-by-hop-identifier    ${hbh}
    ${msgData_aia_ulr}    Replace    ${msgData_aia_ulr}    diameter    end-to-end-identifier    ${ete}
    [Return]    ${msgData_aia_ulr}

Verify Request Response Parameters
    [Arguments]    ${dataToCompare}    ${dataToBeCompared}    ${parentkey}    ${childKey}
    [Documentation]    This keyword is used for verifying the request and response parameters. This keyword takes below arguments
    ...
    ...    ${dataToCompare} - Input JSON file dictionary
    ...    ${dataToBeCompared} - Response received from MME
    ...    ${parentkey} \ - Parent Key of the value to be compared
    ...    ${childKey} - Child Key of the value to be compared
    ...
    ...    This keyword will compare the request and response from MME dictionary value, if the comparision fails then test case would be failed and execution will be terminated.
    ${returnJSONFile}    Run Keyword If    '${dataToCompare}'=='createSession'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/create_session_request.json
    ...    ELSE IF    '${dataToCompare}'=='modifyBearer'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/modify_bearer_request.json
    ...    ELSE IF    '${dataToCompare}'=='deleteSession'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/delete_session_request.json
    ...    ELSE IF    '${dataToCompare}'=='releaseBearer'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/release_access_bearer_request.json
    : FOR    ${index}    ${eachChildKey}    IN ENUMERATE    @{childKey}
    \    ${valueToCompareFromJSON}    Get Child Key Value From Parent Key    ${returnJSONFile}    @{parentKey}[${index}]    ${eachChildKey}
    \    ${returnValueToBeCompared}    Get Child Key Value From Parent Key    ${dataToBeCompared}    @{parentKey}[${index}]    ${eachChildKey}
    \    ${valueToCompareJSON}    Get Element Description    ${eachChildKey}    ${valueToCompareFromJSON}
    \    ${valueToBeCompared}    Get Element Description    ${eachChildKey}    ${returnValueToBeCompared}
    \    Should Match    ${valueToCompareJSON}    ${valueToBeCompared}    Expected ${eachChildKey}: ${valueToCompareJSON}(${valueToCompareFromJSON}), but Received ${eachChildKey}: ${valueToBeCompared}(${returnValueToBeCompared})    values=False

Verify All Occurances of Request Response Parameter
    [Arguments]    ${dataToCompare}    ${dataToBeCompared}    ${key}
    [Documentation]    This keyword is used for verifying all the occurances of request and response of a given key. This keyword takes below arguments
    ...
    ...    ${dataToCompare} - Input JSON file dictionary
    ...    ${dataToBeCompared} - Response received from MME
    ...    ${key} - Key of the value to be compared
    ...
    ...    This keyword will compare the request and response from MME dictionary value, if the comparision fails then test case would be failed and execution will be terminated.
    ${returnJSONFile}    Run Keyword If    '${dataToCompare}'=='createSession'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/create_session_request.json
    ...    ELSE IF    '${dataToCompare}'=='modifyBearer'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/modify_bearer_request.json
    ...    ELSE IF    '${dataToCompare}'=='deleteSession'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/delete_session_request.json
    ...    ELSE IF    '${dataToCompare}'=='releaseBearer'    Load JSON Data From File    ${CURDIR}/../../../MessageTemplates/GTP/release_access_bearer_request.json
    : FOR    ${index}    ${eachKey}    IN ENUMERATE    @{key}
    \    ${valueToCompareFromJSON}    Get All Instance Key Value    ${returnJSONFile}    ${eachKey}
    \    ${returnValueToBeCompared}    Get All Instance Key Value    ${dataToBeCompared}    ${eachKey}
    \    Validate All Occurance Request Response with Description    ${valueToCompareFromJSON}    ${returnValueToBeCompared}    ${eachKey}

Validate All Occurance Request Response with Description
    [Arguments]    ${valueToCompareFromJSON}    ${returnValueToBeCompared}    ${eachKey}
    [Documentation]    This keyword is used for validating the list of expected and actual results. This keyword takes below arguments
    ...
    ...    ${valueToCompareFromJSON} - Input JSON file value list
    ...    ${returnValueToBeCompared} \ - Response received from MME value list
    ...    ${eachKey} - Key of the value to be compared
    ...
    ...    If the comparision of list value fails then test case would be failed and execution will be terminated.
    : FOR    ${index1}    ${eachKey1}    IN ENUMERATE    @{valueToCompareFromJSON}
    \    ${valueToCompareJSON}    Get Element Description    ${eachKey}    ${eachKey1}
    \    ${valueToBeCompared}    Get Element Description    ${eachKey}    @{returnValueToBeCompared}[${index1}]
    \    Should Match    ${valueToCompareJSON}    ${valueToBeCompared}    Expected ${eachKey}: ${valueToCompareJSON}(${eachKey1}), but Received ${eachKey}: ${valueToBeCompared}(@{returnValueToBeCompared}[${index1}])    values=False

Get Element Description
    [Arguments]    ${keyElement}    ${keyToGetValue}
    [Documentation]    This keyword converts the message_type ot interface_type integer in to it's respective description from GTPv2Types.json file. Below arguments are taken as input.
    ...
    ...    ${keyElement} - Either message_type or interface_type
    ...    ${keyToGetValue} - Integer to get description
    ...
    ...    It returns the description.
    ${returnDict}    Run Keyword If    '${keyElement}'=='message_type' or '${keyElement}'=='interface_type'    Load JSON Data From File    ${CURDIR}/../../support_utilities/GTPv2Types.json
    ${keyToGetValue}    Convert to String    ${keyToGetValue}
    ${returnValue}    Get Child Key Value From Parent Key    ${returnDict}    ${keyElement}    ${keyToGetValue}
    [Return]    ${returnValue}

Get GRPC Stats Response Count
    [Arguments]    ${procStat}    ${stringToSearch}
    [Documentation]    This keyword executes the GRPC command and returns the count
    ...
    ...    ${stringToSearch} - String to search for count
    ...
    ...
    ...    ${count} It returns the count of search string
    ${ueCount}    Split Proc Stats    ${procStat}    ${stringToSearch}
    ${ueCount}    Convert to Integer    ${ueCount}
    [Return]    ${ueCount}


