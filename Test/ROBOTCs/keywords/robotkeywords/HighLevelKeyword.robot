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
Documentation     This is a global keyword file which contains all the user defined and pre defined ibararies imported. No *Keywords* should be created in this file.
Library           String
Library           Collections
Library           BuiltIn
Library           OperatingSystem
Library           Process
Library           DateTime
Library           XML
Library           ../../../../Dev/Protocols/GTP/gtpEncoder.py
Library           ../../../../Dev/Protocols/S1AP/s1apTC.py
Library           ../../../../Dev/Protocols/GTP/gtpTC.py
Library           ../../../../Dev/Protocols/Diameter/diameterTC.py
Library           ../../../../Dev/Common/igniteCommonUtil.py
Library           ../../../../Dev/Protocols/NAS/Util/nasUtils.py
Library           ../systemkeywords/JSONLib.py
Library           ../systemkeywords/dictOperations.py
Library           SSHLibrary
