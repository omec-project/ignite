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

import os,sys
import binascii
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Common'))
from protocolMessageTypes import ProtocolMessageTypes as mt
configuration_file = os.path.join(os.path.dirname(__file__),'..', '..', 'Common','configuration.json')
with open(configuration_file) as configuration:
            config_file=json.loads(configuration.read())

s1apMessageDict={
    11:"downlink_nas_transport",
    9:"initial_context_setup_request",
    10:"paging",
    17:"setup_response",
    18:"ue_context_release_request",
    23:"ue_context_release_command"
    }

s1ApCreateContextMessagesList=[mt.authentication_request.name,mt.identity_request.name,mt.attach_accept.name]

def convertIpaddressToHex(value):
    if type(value)==str:
        if len(value.split("."))==4:
            tl_list = []
            ip_list = value.split(".")
            for x in ip_list:
                tl_list.append(int(x))
            address = binascii.hexlify(bytearray(tl_list))
            final_address = str(address.decode())
            return final_address

def transportLayerAddressUpdate(value=None):
    if value == None:
        ip_address = config_file["s1ap"]["ignite_ip"]
    else:
        ip_address = value
    tl_list = []
    ip_list = ip_address.split(".")
    for x in ip_list:
        tl_list.append(int(x))
    address = binascii.hexlify(bytearray(tl_list))
    final_address = "1f"+str(address.decode())
    return final_address
