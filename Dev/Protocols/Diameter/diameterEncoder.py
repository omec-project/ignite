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

from struct import *
from array import *
from binascii import hexlify
import re
from codecs import encode
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

#dirName = os.path.dirname(__file__)
diameterGrammarFile = os.path.join(os.path.dirname(__file__), 'sub_template.txt')

indexValue = 0
bufValue = array('B', [0 for N in range(1000)])

def modifyIp(ip):
	if "." in ip:
	        list1 = ip.split(".")
	list2=[]
	for num in list1:
		list2.append(int(num))
	return list2


def encodeDiameter(data):
	try:
		global indexValue, bufValue
		# Encode Version (1)
		version = data["version"]

		# Set offset for packing length in the end
		len_offset = indexValue
		indexValue +=4

		# Encode flags
		flags = data["flags"]

		# Encode command-code
		command_code = data["command-code"]
		flag_cc = flags<<24 | command_code
		pack_into('!I', bufValue, indexValue, flag_cc)
		indexValue +=4

		# Encode application-id
		application_id = data["application-id"]
		pack_into('!I', bufValue, indexValue, application_id)
		indexValue +=4
		
		# Encode hop-by-hop-identifier
		hbh_identifier = data["hop-by-hop-identifier"]
		pack_into('!4B', bufValue, indexValue, *[int(hbh_identifier[i:i+2], 16) for i in range (0, len(hbh_identifier), 2)])
		indexValue +=4

		# Encode end-to-end-identifier
		ete_identifier = data["end-to-end-identifier"]
		pack_into('!4B', bufValue, indexValue, *[int(ete_identifier[i:i+2], 16) for i in range (0, len(ete_identifier), 2)])
		indexValue +=4
		
		# Encode AVPs
		avps = data["avp"]
			# Loading the template file into a list
		#templateFile = "sub_template.txt"
		file_list = []
		with open(diameterGrammarFile) as file:
			for line in file:
				file_list.append(line)

		encodeDiameterAvps(avps, file_list)
		
		# Encode the header length at len_offset
		length = version<<24 | indexValue
		pack_into('!I', bufValue, len_offset, length)

		ret_index = indexValue
		ret_buf = bufValue
		indexValue = 0
		bufValue = array('B', [0 for N in range(1000)])
		return ret_index, ret_buf
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")



def encodeDiameterAvps(avps, file_list):
	try:
		global indexValue, bufValue
		# Regular Expression for finding in template file
		regEx = "<(.+)>\s*::=\s*<.*:\s*(\d+),\s*(\w+)\s*>"

		# Iterate over the avps in the json
		for avp in avps:
			avp_length = 0
			# Encode the AVP Code
			avp_code = avp["code"]
			pack_into('!I', bufValue, indexValue, avp_code)
			indexValue +=4
			avp_length +=4
			# Encode AVP Flags
			flags = avp["flags"]
			# Encode the AVP Length
			avp_len_offset = indexValue
			indexValue +=4
			avp_length +=4
			# Encode Vendor id, if present
			if flags>96:
				v_id = avp["vendor-id"]
				pack_into('!I', bufValue, indexValue, v_id)
				indexValue +=4
				avp_length +=4

			avp_type=""
			avp_name=""
			# Iterate in the file List to match for the regex		
			for line in file_list:
				match = re.search(regEx, line)
				if match:
					# If the code is found in the matching line,
					# set avp_name and avp_type for encoding the avp
					if avp_code==int(match.group(2)):
						avp_name = match.group(1).lower()
						avp_type = match.group(3).lower()
						break
			# If type of the avp is unsigned32 or integer32, pack in 4 bytes	
			if avp_type=="unsigned32" or avp_type=="integer32":
				avp_value = avp[avp_name]
				pack_into('!I', bufValue, indexValue, avp_value)
				indexValue +=4
				avp_length +=4
		
			# If type of the avp is an Enum, pack in 4 byte
			elif avp_type=="enumerated":
				avp_value = avp[avp_name]
				pack_into('!I', bufValue, indexValue, avp_value)
				indexValue +=4
				avp_length +=4

			# If type of the avp is an address, pack address-type in 2 bytes and address in 4 bytes using the modifyIp method
			elif avp_type=="address" :
				address_type = avp["address-type"]
				pack_into('!H', bufValue, indexValue, address_type)
				indexValue +=2
				avp_length +=2
				avp_value = modifyIp(avp[avp_name])
				pack_into('!4B', bufValue, indexValue, *(i for i in avp_value))
				indexValue +=4
				avp_length +=4
				# Padding needed for 32-bit boundary
				pack_into('!H', bufValue, indexValue, 0)
				indexValue +=2

			# If type is only IP, pack IP-address in 4 bytes using modifyIp
			elif avp_type=="ip":
				avp_value = modifyIp(avp[avp_name])
				pack_into('!4B', bufValue, indexValue, *(i for i in avp_value))
				indexValue +=4
				avp_length +=4
			
			# If type of the avp is UTF8String or String or diameterIdent or diamURI, pack in length/2 bytes
			elif avp_type=="utf8string" or avp_type=="string" or avp_type=="diameteridentity" or avp_type=="diamuri":
				#avp_value = avp[avp_name].encode('hex')
				avp_value = encode(avp[avp_name].encode(), 'hex')
				val_len = len(avp_value)//2
				pack_into('!{}B'.format(val_len), bufValue, indexValue, *[int(avp_value[i:i+2], 16) for i in range(0, len(avp_value), 2)])
				indexValue +=val_len
				avp_length +=val_len
				# Padding required if length is not a multiple of 4 octets
				octets = avp_length%4
				if octets!=0:
					padding_length = 4 - octets
					padding_list = []
					for i in range(0, padding_length):
						padding_list.append(0)
					pack_into('!{}B'.format(padding_length), bufValue, indexValue, *(i for i in padding_list))
					indexValue +=padding_length

			# If type of the avp is Octet String, pack it as direct hex
			elif avp_type=="octetstring":
				avp_value = avp[avp_name]
				val_len = len(avp_value)//2
				pack_into('!{}B'.format(val_len), bufValue, indexValue, *[int(avp_value[i:i+2], 16) for i in range(0, len(avp_value), 2)])
				indexValue +=val_len
				avp_length +=val_len
							# Padding required if length is not a multiple of 4 octets
				octets = avp_length%4
				if octets!=0:
					padding_length = 4 - octets
					padding_list = []
					for i in range(0, padding_length):
						padding_list.append(0)
					pack_into('!{}B'.format(padding_length), bufValue, indexValue, *(i for i in padding_list))
					indexValue +=padding_length

			# If type of the avp is grouped, it implies there are sub avps
			elif avp_type=="grouped":
				sub_avp = avp[avp_name]
				i = indexValue
				# Recursively call the avp encoder over sub-avps
				encodeDiameterAvps(sub_avp, file_list)
				avp_length +=(indexValue-i)
			
			# Encode the avp length at the avp_len_offset
			pack_length = flags<<24 | avp_length
			pack_into('!I', bufValue, avp_len_offset, pack_length)
			
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")

