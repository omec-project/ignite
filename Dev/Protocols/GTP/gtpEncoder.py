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
from codecs import encode
from gtpGrammar import workbook
import re
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','Logger'))
import igniteLogger

index = 0
buf = array('B', [0 for N in range(1000)])

ieLength = 0

def modifyIpv4(ip):
        if "." in ip:
                list1 = ip.split(".")
        list2=[]
        for num in list1:
                list2.append(int(num))
        return list2



def encodeGTP(data,ie_location):
	try:
		global index, buf
		index = 0
		buf = array('B', [0 for N in range(1000)])

		# encode the flags
		# including ver, p, teid flags and Mp
		flags = data["flags"]
		pack_into('!B', buf, index, *[int(flags[0:], 16)])
		index += 1

		# encode message-type
		msg_type = data["message_type"]
		pack_into('!B', buf, index, msg_type)
		index += 1

		# set offset for encoding length at the end
		len_offset = index
		index += 2

		# encode TEID
		if "teid" in data:
			teid = data["teid"]
			pack_into('!I', buf, index, teid)
			index += 4

		# encode Sequence-Number & Spare
		seq = hex(data["sequence_number"])[2:]
		spare = hex(data["spare"])[2:]
		seq = '0'*(6-len(seq))+seq
		seq_spare = seq + spare
		pack_into('!4B', buf, index, *[int(seq_spare[i:i+2], 16) for i in range(0, len(seq_spare), 2)])
		index += 4

	# encode the IEs by calling the encodeIE function
		ies = data["information_elements"]
		for ie in ies:
			packet_len = encodeIE(ie,ie_location)

	# encode the length at the len_offset
		pack_into('!H', buf, len_offset, index-4)

		return buf, index
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")



# Method to encode the IEs
def encodeIE(test_dict,ie_location):
	try:

		global index, buf, ieLength

		
		sheet = workbook.sheet_by_index(2)

		rows = sheet.nrows
		cols = sheet.ncols
		
		# Defining Regular-Expressions for matching strings with excel cell data
		reg_ex1 = "Type\s*=\s*(\d+)\s*\((.*)\)"
		reg_ex2 = "(.*):Type\[(\w*)\].*"
		reg_ex3 = "IE Definition End\s*:(.*)"

		if test_dict["ie_type"] in ie_location:
			ie_type = test_dict["ie_type"]
			ie_type_data = ie_location[ie_type]
			lrow = ie_type_data["lrow"]
			hrow = ie_type_data["hrow"]
			lcol = ie_type_data["lcol"]
			hcol = ie_type_data["hcol"]
			pack_into('!B', buf, index, test_dict["ie_type"])
			index += 1
			len_offset = index
			index += 2
			flags = test_dict["spare"] << 4 | test_dict["instance"]
			pack_into('!B', buf, index, flags)
			index += 1
		
		# Iterating over the matched IE only
		header_index = index
		for row in range(lrow, hrow):
				cell = sheet.cell(row, lcol)
				val = 0
				match = re.search(reg_ex2, str(cell.value))
				# If it is the entire cell containing a field and data_type, we can pack directly
				if match:
					name =  str(match.group(1).lower())
					data_type = str(match.group(2).lower())
					dec_bytes = 0
			# If datatype is decimal, we need to refer previous cell for size of the field
			# Decimal type can be packed in B, H, I etc.
					if data_type == "decimal":
						byte_cell = sheet.cell(row, lcol-1)
						byte_reg_ex = "(\d+)\s*to\s*(\d+)"
						match_byte = re.search(byte_reg_ex, str(byte_cell.value))
						if match_byte:
							dec_bytes = int(match_byte.group(2))-int(match_byte.group(1))+1
						else:
							dec_bytes = 1
		
			# if Grouped IE, recursive call of this method
					elif data_type == "grouped":
						i = index
						sub_ies = test_dict[name]
						for sub_ie in sub_ies:
							encodeIE(sub_ie,ie_location)
			# If our JSON contains the field in the cell, we call the method to pack this data
					if str(name) in test_dict:
						typeEncoder(test_dict[name], data_type, dec_bytes)
						continue
		
				# If above is not the case, we need to pack columns bitwise
				else:
					bit_count = 1
			# Iterating over the columns
					for col in range(lcol, hcol):
						cell = sheet.cell(row, col)
						# If the next cell is empty, either merged cell or last cell
						if sheet.cell(row, col+1).value == "":
							if col+1==hcol:
								cell = sheet.cell(row, col-bit_count+1)
								if cell.value == "Spare":
									val | 0
								else:
									val = val | test_dict[cell.value.lower()]
								bit_count = 1
								break
							else:
								bit_count += 1
						# If the next cell has data, this cell needs to be calculated in bits using bit_count
						else:
							cell = sheet.cell(row, col-bit_count+1)
							if cell.value == "Spare":
								val = val | 0
							else:
								val = val | test_dict[cell.value.lower()]<<(10-col)
							bit_count = 1
							continue
			# Finally call method to pack
					data_type = "decimal"
					typeEncoder(val, data_type, 1)
		
		# Logic to encode the IE length at the offset
		end_index = index
		if data_type != "grouped":
			ieLength = end_index - header_index
		else:
			ieLength = end_index - i

		# Pack the ie length
		pack_into('!H', buf, len_offset, ieLength)
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
	
	

# Method to pack data according to datatypes	
def typeEncoder(value, data_type, dec_bytes=0):
	try:

		global index, buf, ieLength

		reg_ex = "uint8array(\d+)"
		match = re.search(reg_ex, data_type)
		

		# If datatype is decimal, pack as B, H or I depending on dec_bytes
		if data_type == "decimal":
			if int(dec_bytes) == 1:
				pack_into('!B', buf, index, int(value))
				index += 1
			elif int(dec_bytes) == 2:
				pack_into('!H', buf, index, int(value))
				index += 2
			elif int(dec_bytes) == 4:
				pack_into('!I', buf, index, int(value))
				index += 4

		# Packing for type hex
		elif data_type == "hex":
			pack_into('!{}B'.format(len(value)//2), buf, index, *[int(value[i:i+2], 16) for i in range(0, len(value), 2)])
			index += len(value)//2

		# Packing for type unsigned32
		elif data_type == "unsigned32":
			pack_into ('!I', buf, index, int(value))
			index += 4

		# For packing IP address, call method to convert formatting of IP
		elif data_type == "ipaddressv4":
			ipv4 = modifyIpv4(value)
			pack_into('!4B', buf, index, *(i for i in ipv4))
			index += 4

		# Logic defined for packing type digitregister (eg. IMSI, MSISDN, MEI)
		elif data_type == "digitregister":
					pack_value = ""
					if len(value)%2 != 0:
						value = value+"f"
					for i in range(0, len(value), 2):
						pack_value = pack_value + value[i+1] + value[i]
					pack_into('!{}B'.format(len(pack_value)//2), buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += len(pack_value)//2

		# Pack cgi
		elif data_type == "cgifield":
			mcc = value["mcc"]
			mnc = value["mnc"]
			if len(mnc) == 2:
				mnc = mnc+"f"

			lac = value["location_area_code"]
			ci = value["cell_identity"]
			pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
			pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
			index += 3
			pack_into('!H', buf, index, int(lac))
			index += 2
			pack_into('!H', buf, index, int(ci))
			index += 2

		# Pack sai
		elif data_type == "saifield":
					mcc = value["mcc"]
					mnc = value["mnc"]
					if len(mnc) == 2:
							mnc = mnc+"f"

					lac = value["location_area_code"]
					sac = value["service_area_code"]
					pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
					pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += 3
					pack_into('!H', buf, index, int(lac))
					index += 2
					pack_into('!H', buf, index, int(sai))
					index += 2

		# Pack rai
		elif data_type == "raifield":
					mcc = value["mcc"]
					mnc = value["mnc"]
					if len(mnc) == 2:
							mnc = mnc+"f"

					lac = value["location_area_code"]
					rac = value["routing_area_code"]
					pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
					pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += 3
					pack_into('!H', buf, index, int(lac))
					index += 2
					pack_into('!H', buf, index, int(rac))
					index += 2

		# Pack tai
		elif data_type == "taifield":
					mcc = value["mcc"]
					mnc = value["mnc"]
					if len(mnc) == 2:
							mnc = mnc+"f"

					tac = value["tracking_area_code"]
					pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
					pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += 3
					pack_into('!H', buf, index, int(tac))
					index += 2

		# Pack ecgi
		elif data_type == "ecgifield":
					mcc = value["mcc"]
					mnc = value["mnc"]
					if len(mnc) == 2:
							mnc = mnc+"f"

					ecgi = value["eutran_cell_id"]
					pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
					pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += 3
					pack_into('!I', buf, index, int(ecgi))
					index += 4

		# Pack lai
		elif data_type == "laifield":
					mcc = value["mcc"]
					mnc = value["mnc"]
					if len(mnc) == 2:
							mnc = mnc+"f"

					lac = value["location_area_code"]
					pack_value = mcc[1]+mcc[0]+mnc[2]+mcc[2]+mnc[1]+mnc[0]
					pack_into('!3B', buf, index, *[int(pack_value[i:i+2], 16) for i in range(0, len(pack_value), 2)])
					index += 3
					pack_into('!H', buf, index, int(lac))
					index += 2

		# Pack apn
		elif data_type == "apnfield":
			for label in value.split("."):
				label_len = len(label)
				pack_into('!B', buf, index, label_len)
				index += 1
				label = encode(label.encode(), 'hex')
				pack_into('!{}B'.format(len(label)//2), buf, index, *[int(label[i:i+2], 16) for i in range(0, len(label), 2)])
				index += len(label)//2
					
		# For packing sstring type data
		elif match:
				value = value.encode()
				pack_into('!{}B'.format(len(value)//2), buf, index, *[int(value[i:i+2], 16) for i in range(0, len(value), 2)])
				index += len(value)//2
				
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")
		

