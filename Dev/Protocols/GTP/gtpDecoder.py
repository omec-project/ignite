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
from binascii import *
from codecs import decode
import re
import os, sys
from gtpGrammar import workbook
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','Logger'))
import igniteLogger

data = {}
index = 0
length = 0

def makeIp(tup1):
	str1=''
	for num in tup1:
		str1 = str1+str(num)+"."
	return str1[:-1]



def decodeGTP(buf,ie_location):
	try:
		global data, index, length
		data = {}
		index = 0
		length = 0

		# decode flags
		#including ver, p&teid flags and Mp
		flags = unpack_from('!B', buf, index)
		index += 1
		data["flags"] = "".join([("%x" %i).zfill(2) for i in flags])
		
		# decode message type
		msg_type = unpack_from('!B', buf, index)[0]
		index += 1
		data["message_type"] = msg_type
		
		# decode length 
		length = unpack_from('!H', buf, index)[0]
		index += 2
		
		if msg_type!=1 and msg_type!=2:
			# decode teid
			teid = unpack_from('!I', buf, index)[0]
			index += 4
			length -= 4
			data["teid"] = teid
		
		# decode Sequence Number
		seq = unpack_from('!3B', buf, index)
		index += 3
		length -= 3
		seq_no = "".join([("%x" %i).zfill(2) for i in seq])
		data["sequence_number"] = int(seq_no, 16)

		# decode the Spare bytes
		spare = unpack_from('!B', buf, index)
		index += 1
		length -= 1
		spare_val = "".join([("%x" %i).zfill(2) for i in spare])
		data["spare"] = int(spare_val, 16)

		#decode the IEs by invoking the method
		if length > 0:
			decodeIE(buf,ie_location)


		# return the final dictionary and the length
		return data, index
		
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")



# Method to decode the IEs
def decodeIE(buf,ie_location):
	try:
		global data, index, length
		sheet = workbook.sheet_by_index(2)
		rows = sheet.nrows
		cols = sheet.ncols
		reg_ex1 = "Type\s*=\s*(\d+)\s*\((.*)\)"
		reg_ex2 = "(.*):Type\[(\w*)\].*"
		reg_ex22 = "(.*):Type\[(\w*)\]:Condition\[(.*)\].*"
		reg_ex3 = "IE Definition End\s*:(.*)"

		while length > 0:
			# make a list of IEs if already not present
			if "information_elements" not in data:
				data["information_elements"] = []
			
			#Initialize an empty dictionary for each IE
			ie_data = {}

			# decode the ie_type from the buf
			ie_type = unpack_from('!B', buf, index,)[0]
			index += 1
			length -= 1
			ie_data["ie_type"] = ie_type
			if ie_type in ie_location:
				ie_type_data = ie_location[ie_type]
				lrow = ie_type_data["lrow"]
				hrow = ie_type_data["hrow"]
				lcol = ie_type_data["lcol"]
				hcol = ie_type_data["hcol"]
				ie_length = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				spare_instance = unpack_from('!B', buf, index)[0]
				index += 1
				length -= 1
				instance = spare_instance & 0xff
				spare = spare_instance >> 4 & 0xff
				ie_data["spare"] = spare
				ie_data["instance"] = instance

			# loop for the particula ie details
			for row in range(lrow, hrow):
				cell = sheet.cell(row, lcol)
				match = re.search(reg_ex2, str(cell.value))
				match1 = re.search(reg_ex22, str(cell.value))
				# if reg_ex2 matches, capture the ie_name and ie_dataType from the cell
				name = ""
				data_type = ""
				if match:
					name =  str(match.group(1).lower())
					data_type = str(match.group(2).lower())
					include_field = 0
					dec_bytes = 0
					# Since decimal can be B, H, I etc; need to get that info from cell before
					if data_type == "decimal":
						byte_cell = sheet.cell(row, lcol-1)
						# reg_ex to match x to y where y-x+1 gives B, H or I
						byte_regEx = "(\d+)\s*to\s*(\d+)"
						match_byte = re.search(byte_regEx, str(byte_cell.value))
						if match_byte:
							dec_bytes = int(match_byte.group(2))-int(match_byte.group(1))+1
						else:
							dec_bytes = 1

					# if reg_ex22 matches, conditional fields will come in
					if match1:
						# get the condition from the cell
						condition = match1.group(3)
						# define condition type regExs.
						# Could be required to update, if new IEs with other type conditions come up
						condition_reg_ex1 = "(.+)\s*==\s*(\d+)"
						condition_reg_ex2 = "(.+)\s*==\s*(\d+)\s*or\s*(.+)\s*==\s*(\d+)"
						condition_match1 = re.search(condition_reg_ex1, condition)
						condition_match2 = re.search(condition_reg_ex2, condition)
						# check for more than 1 condition in the cell from the dictionary
						if condition_match1 and condition_match2:
							if ie_data[condition_match2.group(1).lower()[5:-1]] == int(condition_match2.group(2)) or ie_data[condition_match2.group(3).lower()[5:-1]] == int(condition_match2.group(4)):
								include_field = 1
						# check for 1 condition in the cell from the dictionary
						elif condition_match1:
							if ie_data[condition_match1.group(1).lower()[5:-1]] == int(condition_match1.group(2)):
								include_field = 1
						# if simple condition given, just check if value = 1
						else:
							if ie_data[condition[5:].lower()] == 1:
								include_field = 1

					# if reg_ex22 is not matchd, it means no extra conditions and the cell filed can be included in dictionary
					else:
						include_field = 1

				
					# if include_field flag is 1, decode into dictionary
					if include_field == 1:
						size_reg_ex1 = "(\d+)\s*to\s*(\d+)"
						size_reg_ex2 = "(\w+)\s*to\s*(\w+)\+(\d+)"
						size_reg_ex3 = "variable.*"
						size_cell = sheet.cell(row, lcol-1)
						size = str(size_cell.value)
						match_size1 = re.search(size_reg_ex1, size)
						match_size2 = re.search(size_reg_ex2, size)
						match_size3 = re.search(size_reg_ex3, size)
						if match_size1:
							field_length = int(match_size1.group(2)) - int(match_size1.group(1))+1
						elif match_size2:
							field_length = int(match_size2.group(3))+1
						elif match_size3:
							field_length = ie_length
						else:
							field_length = 1
						
						typeDecoder(buf, ie_data, name, data_type, field_length, dec_bytes)


				# When reg_ex2 did not match, columns need to be added bit-wise
				else:
					# unpack the entire Byte from the buffer
					val = unpack_from('!B', buf, index)[0]
					index += 1
					length -= 1
					# variable to count bits
					bit_count = 1
					# iterating over the columns
					for col in range(lcol, hcol):
						cell = sheet.cell(row, col)
						# Check if the next cell is empty (meaning merged cell, so bit_count will increase)
						if sheet.cell(row, col+1).value == "":
							# If it is last column, the above logic will not hold true
							if col+1==hcol:
								cell = sheet.cell(row, col-bit_count+1)
								binary = "0b"
								# Building up a binary value to get operand to perform bitwise operation
								for i in range (0, bit_count):
									binary = binary + "1"
								operand = int(binary, 2)
								field_value = val & operand
								# add the data to the field
								ie_data[cell.value.lower()] = field_value
								bit_count = 1
								break
		
							# If not, simply increase bit_count
							else:
								bit_count += 1
						# If next cell is not empty, this value needs to be evaluated according to bit_count
						else:
							cell = sheet.cell(row, col-bit_count+1)
							binary = "0b"
							# Building up a binary value to perform bitwise operation
							for i in range (0, bit_count):
								binary = binary + "1"
							operand = int(binary, 2)
							field_value = (val>>(8-(col-2))) & operand
							# add the data to the field
							ie_data[cell.value.lower()] = field_value
							bit_count = 1
							continue

			data["information_elements"].append(ie_data)
			
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")


# Method to decode data according to dataTypes
def typeDecoder(buf, ie_data, name, data_type, ie_length, dec_bytes=0):
	try:
		global data, index, length
		reg_ex = "uint8array(\d+)"
		match = re.search(reg_ex, data_type)

		if data_type == "decimal":
			if int(dec_bytes) == 1:
				ie_data[name] = unpack_from('!B', buf, index)[0]
				index += 1
				length -= 1
			elif int(dec_bytes) == 2:
				ie_data[name] = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
			elif int(dec_bytes) == 4:
				ie_data[name] = unpack_from('!I', buf, index)[0]
				index += 4
				length -= 4

		elif data_type == "hex":
				value = unpack_from('!{}B'.format(ie_length), buf, index)
				ie_data[name] = "".join([("%x" %i).zfill(2) for i in value])
				index += ie_length
				length -= ie_length

		elif data_type == "unsigned32":
				ie_data[name] = unpack_from('!I', buf, index)[0]
				index += 4
				length -= 4

		elif data_type == "ipaddressv4":
				value=unpack_from('!4B',buf,index)
				ie_data[name] = makeIp(value)
				index += 4
				length -= 4

		elif data_type == "digitregister":
				u_val = unpack_from('!{}B'.format(ie_length), buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				value = ""
				for i in range(0, len(unpack_value), 2):
					value = value + unpack_value[i+1] + unpack_value[i]
				value = value.replace("f", "")
				ie_data[name] = value
				index += ie_length
				length -= ie_length

		elif data_type == "cgifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				lac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ci = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["location_area_code"] = lac
				ie_data[name]["cell_identity"] = ci

		elif data_type == "saifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				lac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				sac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["location_area_code"] = lac
				ie_data[name]["service_area_code"] = sac

		elif data_type == "raifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				lac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				rac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["location_area_code"] = lac
				ie_data[name]["routing_area_code"] = rac

		elif data_type == "taifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				tac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["tracking_area_code"] = tac

		elif data_type == "ecgifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				ecgi = unpack_from('!I', buf, index)[0]
				index += 4
				length -= 4
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["eutran_cell_id"] = ecgi

		elif data_type == "laifield":
				u_val = unpack_from('!3B', buf, index)
				unpack_value = "".join([("%x" %i).zfill(2) for i in u_val])
				index += 3
				length -= 3
				mcc = unpack_value[1]+unpack_value[0]+unpack_value[3]
				mnc = unpack_value[5]+unpack_value[4]+unpack_value[2]
				mnc = mnc.replace("f", "")
				lac = unpack_from('!H', buf, index)[0]
				index += 2
				length -= 2
				ie_data[name] = {}
				ie_data[name]["mnc"] = mnc
				ie_data[name]["mcc"] = mcc
				ie_data[name]["location_area_code"] = lac

		elif data_type == "apnfield":
				apn_val = ""
				while ie_length>0:
						label_len = unpack_from('!B', buf, index)[0]
						index += 1
						length -= 1
						ie_length -= 1
						label = unpack_from('!{}B'.format(label_len), buf, index)
						labe_val = "".join([("%x" %i).zfill(2) for i in label])
						labe_val = decode(labe_val, 'hex').decode()
						index += label_len
						length -= label_len
						ie_length -= label_len
						if apn_val == "":
								apn_val += labe_val
						else:
								apn_val = apn_val + "." + labe_val

				ie_data["apn"] = apn_val


		elif match:
				value = unpack_from('{}B'.format(ie_length), buf, index)
				ie_data[name] = "".join([("%x" %i).zfill(2) for i in value])
				index += ie_length
				length -= ie_length
				
	except Exception as e:
		igniteLogger.logger.info("Printing exception : "f"{e}")

			
