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
from codecs import decode
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Logger'))
import igniteLogger

#dirName = os.path.dirname(__file__)
diameterGrammarFile = os.path.join(os.path.dirname(__file__), 'sub_template.txt')

data = {}
index = 0

def makeIp(tup1):
    str1=''
    for num in tup1:
        str1 = str1+str(num)+"."
    return str1[:-1]

def decodeDiameter(buf):
	try:
		global data,index, diameterGrammarFile
		#reset data & index
		data = {}
		index = 0
		#decode version and length
		ver_len=unpack_from('!I',buf,index)[0]
		len_offset = ver_len & 0xffffff

		version = (ver_len>>24) & 0xff
		data["version"] = version
		index+=4
		len_offset-=4

		#decode flags and code
		flags_code=unpack_from('!I',buf,index)[0]
		code=flags_code & 0xffffff
		flags = (flags_code>>24) & 0xff
		data["command-flags"]=flags
		data["command-code"]=code
		index+=4
		len_offset-=4

		#decode application-id
		app_id=unpack_from('!I',buf,index)[0]
		data["application_id"]=app_id
		index+=4
		len_offset-=4

		#decode hop-by-hop identifier
		hbh_identifier=unpack_from('!4B',buf,index)
		index+=4
		len_offset-=4

		data["hop-by-hop-identifier"]="".join([("%x" %i).zfill(2) for i in hbh_identifier])

			#decode end-to-end identifier
		ete_identifier=unpack_from('!4B',buf,index)
		index+=4
		len_offset-=4

		data["end-to-end-identifier"]="".join([("%x" %i).zfill(2) for i in ete_identifier])

			# Loading the template file into a list
		#templateFile = "sub_template.txt"
		file_list = []
		with open(diameterGrammarFile) as file:
			for line in file:
				file_list.append(line)

			#decode avps
		if len_offset>0:
			decodeDiameterAvps(data,buf,file_list)

		
		ret_index = index
		ret_data = {"diameter":{"msg":data}}
		index = 0
		data = {}
		return ret_index,ret_data
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
		

def decodeDiameterAvps(data,buf,file_list):
	try:
		global index
		reg_ex = "<(.+)>\s*::=\s*<.*:\s*(\d+),\s*(\w+)\s*>"

		alen_offset = len(buf[index:])


		while(alen_offset>0):
			if "avp" not in data:
				data["avp"]=[]

			avp_data={}
			code=unpack_from('!I',buf,index)[0]
			avp_data["code"]=code
			index+=4
			alen_offset-=4

			aflags_alength = unpack_from('!I',buf,index)[0]
			alength=aflags_alength & 0xffffff
			aflags = (aflags_alength>>24) & 0xff

			index+=4
			alen_offset-=4
			alength-=8

			avp_data["flags"]=aflags
			
			if aflags>96:
				v_id = unpack_from('!I',buf,index)[0]
				avp_data["avp-vendor-id"]=v_id
				index+=4
				alen_offset-=4
				alength-=4
			
			
			avp_type=""
			avp_name=""
					# Iterate in the file List to match for the reg_ex
			for line in file_list:
				match = re.search(reg_ex, line)
				if match:
									# If the code is found in the matching line,
									# set avp_name and avp_type for encoding the avp
					if code==int(match.group(2)):
						avp_name = match.group(1).lower()
						avp_type = match.group(3).lower()
						break

			if avp_type=="unsigned32" or avp_type=="integer32":
				value = unpack_from('!I',buf,index)[0]
				index+=4
				alen_offset-=4
				alength-=4

				avp_data[avp_name] = value
		

			elif avp_type=="enumerated":
				value = unpack_from('!I',buf,index)[0]
				index+=4
				alen_offset-=4
				alength-=4

				avp_data[avp_name] = value
			
			elif avp_type=="address" :
				value=unpack_from('!H',buf,index)[0]
				index+=2
				alen_offset-=2
				alength-=2

				avp_data["host-ip-type"] = value
				value=unpack_from('!4B',buf,index)
				index+=4
				alen_offset-=4
				alength-=4

				padding_length=2
				index+=padding_length
				alen_offset-=padding_length
				alength-=padding_length
				
				avp_data[avp_name]=makeIp(value)

			elif avp_type=="ip":
				value=unpack_from('!4B',buf,index)
				index+=4
				alen_offset-=4
				alength-=4

				avp_data[avp_name] = makeIp(value)

			elif avp_type=="utf8string" or avp_type=="string" or avp_type=="diameteridentity" or avp_type=="diamuri":
				value=unpack_from('!{}B'.format(alength),buf,index)
				padding_length=0
				if ((alength+8)%4)!=0:
					padding_length= 4 - ((alength+8)%4)

				index+=int(alength+padding_length)

				alen_offset-=int(alength+padding_length)
				alength-=alength

				#avp_data[avp_name]="".join([("%x" %i).zfill(2) for i in value]).decode("hex")
				avp_data[avp_name]="".join([("%x" %i).zfill(2) for i in value])
				avp_data[avp_name]= decode(avp_data[avp_name], 'hex').decode()

			elif avp_type=="octetstring":
				value=unpack_from('!{}B'.format(alength),buf,index)
				padding_length=0

				if((alength+8)%4)!=0:
									padding_length= 4 - ((alength+8)%4)
					#next_octet=((alength+8)/4)+1
					#padding_length=((next_octet)*4)-(alength+8)

				index+=int(alength+padding_length)
				alen_offset-=int(alength+padding_length)
				alength-=alength

				avp_data[avp_name]="".join([("%x" %i).zfill(2) for i in value])

			elif avp_type=="grouped":
						# Recursively call the avp decoder over sub-avps

				decodeDiameterAvps(avp_data,buf[:(index+alength)], file_list)
				avp_data[avp_name]=avp_data["avp"]
				del avp_data["avp"]	

				alen_offset-=alength
				alength-=alength
			
			data["avp"].append(avp_data)
			
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
