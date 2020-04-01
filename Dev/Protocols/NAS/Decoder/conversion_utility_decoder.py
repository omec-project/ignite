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

import binascii

def hexstrToAscii(hexStr):
	asciiStr = bytearray.fromhex(hexStr).decode()
	return asciiStr.strip(' \t\r\n\0')
	
def byteToJsonConversion(end_bit,start_bit,output_field,byte_to_json,max_size):

	mask=""
	integer_value=int(output_field,16)	
	range_value = (max_size * 8) - 1
	
	for i in range(range_value,-1,-1):
		if(i<=start_bit and i>=end_bit):
			mask=mask+"1"
		else:
			mask=mask+"0"
	integer_mask=int(mask,2)
	anded_value=integer_value & integer_mask
	final_value=str(anded_value >> end_bit)
	
	if(final_value in byte_to_json):
		return(byte_to_json[final_value])		
	else:
		return final_value
 
def checkOptional(format_of_field,msg_field_grammar,output_list):

	if len(output_list) == 0:
		return False

	if('T' in msg_field_grammar['format']):
		max_size = msg_field_grammar["max_size"] if ("max_size" in msg_field_grammar) else 1
		if(max_size == 1):
			end_bit=msg_field_grammar["end_bit"] if ("end_bit" in msg_field_grammar) else 4
		else:
			end_bit = 0
		start_bit=msg_field_grammar["start_bit"] if ("start_bit"in msg_field_grammar) else 7
		byte_to_json=msg_field_grammar["byte_to_json"] if ("byte_to_json" in msg_field_grammar) else {}
		if('TV' in msg_field_grammar['format']):
			type_id = output_list[0]
		elif('TLV' in msg_field_grammar['format']):
			type_id = output_list[0]
		
		if(str(type_id) != str(msg_field_grammar["type_id"])):
			return False
	return True
