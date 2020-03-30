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
Resource          HighLevelKeyword.robot

*** Keywords ***
Split MME Procedure Statistics String
    [Arguments]    ${procstatoutput}    ${stringbefore}    ${stringafter}
    [Documentation]    This keyword is used for spliting the procedure output and gives in return UE Attach Count.
    ...
    ...    Input Arguments: ${procstatoutput}, ${stringbefore}, ${stringafter}
    ...
    ...    Return Value: ${ueAttachCount}
    ${pre}    ${post}    Split String    ${procstatoutput}    ${stringafter}
    ${pre1}    ${post1}    Split String    ${pre}    ${stringbefore}
    @{stringOut1}    Split String    ${post1}    \    1
    @{stringOut2}    Split String    @{stringOut1}[1]    :
    @{stringOut}    Create List
    : FOR    ${item}    IN    @{stringOut2}
    \    ${item1}    Strip String    ${item}
    \    Append to List    ${stringOut}    ${item1}
    ${len}    Get Length    ${stringOut}
    ${arr}    Evaluate    ${len}-1
    ${countout}    Set Variable If    ${len}>=2    @{stringOut}[${arr}]    @{stringOut}[0]
    ${ueAttachCount}    Strip String    ${countout}
    [Return]    ${ueAttachCount}

Edit Test Suite or Test Case Name
    [Arguments]    ${name}
    [Documentation]    This Keyword will format the Test Suite or Test Case Name, to be used for generating log files.
    ...
    ...    Input Arguments
    ...
    ...    ${name}: Either Testcase or Suite to be provided as input
    ...
    ...    Return value: ${suiteortcname}
    ${suiteortcname}    Set Variable If    '${name}'=='Testcase'    ${TEST NAME}    ${SUITE NAME}
    ${suiteortcname}    Strip String    ${suiteortcname}
    ${suiteortcname}    Replace String    ${suiteortcname}    :    ${EMPTY}
    ${suiteortcname}    Replace String    ${suiteortcname}    ${SPACE}    \_
    [Return]    ${suiteortcname}
