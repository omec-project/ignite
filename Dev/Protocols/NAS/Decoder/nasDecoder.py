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


import os, sys
import json
import field_validation_decoder as fvd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logger'))
import igniteLogger

HOME_DIR = os.path.dirname(__file__)
MESSAGE_GRAMMAR = os.path.join(HOME_DIR, '..', 'Grammar', 'message_grammar.json')
FEILD_GRAMMAR = os.path.join(HOME_DIR, '..', 'Grammar', 'field_grammar.json')


def getSecurityHeaderType(hex_nas_data_list):
	'''Extract first byte - Security Header Type + Protocol Discriminator
	                        <-----bits8-5----->      <-----bits4-1----->'''
	
	security_header_type_byte_value = int(hex_nas_data_list[0],16)	
	SECURITY_HEADER_TYPE_MASK = 240 # 0xF0 or 11110000
	security_header_type_value = (security_header_type_byte_value & SECURITY_HEADER_TYPE_MASK) >> 4
	return security_header_type_value

def getProtocolDiscriminator(hex_nas_data_list):
	protocol_discriminator_byte_value = int(hex_nas_data_list[6], 16)
	PROTOCOL_DISCRIMINATOR_MASK = 15  # 000F or 00001111
	protocol_discriminator_value = (protocol_discriminator_byte_value & PROTOCOL_DISCRIMINATOR_MASK)
	return protocol_discriminator_value
	
def decode(nasDataHexStr):
	try:

		hex_nas_data_list = [nasDataHexStr[i:i+2] for i in range(0,len(nasDataHexStr),2)]
		
		nas_field_grammar = open(FEILD_GRAMMAR,'r')
		nas_fields = json.load(nas_field_grammar)
		nas_field_grammar.close()
		
		security_header_json_types = nas_fields['security_header_type']['byte_to_json']

		mobmgmt_msg_type_json_type = nas_fields['mobility_mgmt_message_type']['byte_to_json']
		
		# Get Security Header Type
		security_header_hype = security_header_json_types[str(getSecurityHeaderType(hex_nas_data_list))]
		
		msg_type_str = ""
		message_type = 0


		if security_header_hype == "plain_nas_message_not_security_protected":
			# 2nd Byte is the Message Type
			message_type = int(hex_nas_data_list[1], 16)

		else:
			protocol_discriminator_json_type = nas_fields['protocol_discriminator']['byte_to_json']
			protocol_discriminator = protocol_discriminator_json_type[str(getProtocolDiscriminator(hex_nas_data_list))]
			if protocol_discriminator == "eps_session_management_messages":
				message_type = int(hex_nas_data_list[8], 16)
			else:
				# 8th Byte is the Message Type for Security protected messages
				message_type = int(hex_nas_data_list[7], 16)
		
		msg_type_str = mobmgmt_msg_type_json_type[str(message_type)]
		
		decoded_output = fvd.convertByteToJson(hex_nas_data_list,msg_type_str)
		
		return 	json.loads(decoded_output)
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
	


